use android_activity::AndroidApp;
use winit::event_loop::EventLoop;
use winit::application::ApplicationHandler;
use winit::event::WindowEvent;
use winit::window::Window;
use egui_wgpu::wgpu;
use std::sync::Arc;

#[unsafe(no_mangle)]
fn android_main(app: AndroidApp) {
    use winit::platform::android::EventLoopBuilderExtAndroid;
    
    let event_loop = EventLoop::builder()
        .with_android_app(app)
        .build()
        .unwrap();
    
    let mut app_state = AppState::default();
    event_loop.run_app(&mut app_state).unwrap();
}

#[derive(Default)]
struct AppState {
    window: Option<Arc<Window>>,
    egui_ctx: Option<egui::Context>,
    egui_winit: Option<egui_winit::State>,
    egui_renderer: Option<egui_wgpu::Renderer>,
    surface: Option<wgpu::Surface<'static>>,
    device: Option<wgpu::Device>,
    queue: Option<wgpu::Queue>,
    surface_config: Option<wgpu::SurfaceConfiguration>,
}

impl ApplicationHandler for AppState {
    fn resumed(&mut self, event_loop: &winit::event_loop::ActiveEventLoop) {
        let window_attributes = Window::default_attributes();
        let window = Arc::new(event_loop.create_window(window_attributes).unwrap());
        
        // Setup rendering
        let instance = wgpu::Instance::default();
        let surface = instance.create_surface(window.clone()).unwrap();
        let adapter = pollster::block_on(instance.request_adapter(&wgpu::RequestAdapterOptions {
            power_preference: wgpu::PowerPreference::default(),
            compatible_surface: Some(&surface),
            force_fallback_adapter: false,
        })).unwrap();
        
        let (device, queue) = pollster::block_on(adapter.request_device(
            &wgpu::DeviceDescriptor::default(),
            None,
        )).unwrap();
        
        let size = window.inner_size();
        let surface_config = surface.get_default_config(&adapter, size.width, size.height).unwrap();
        surface.configure(&device, &surface_config);
        
        let egui_ctx = egui::Context::default();
        let egui_winit = egui_winit::State::new(
            egui_ctx.clone(),
            egui::ViewportId::ROOT,
            &window,
            None,
            None,
            None
        );
        let egui_renderer = egui_wgpu::Renderer::new(&device, surface_config.format, None, 1, false);
        
        self.window = Some(window);
        self.egui_ctx = Some(egui_ctx);
        self.egui_winit = Some(egui_winit);
        self.egui_renderer = Some(egui_renderer);
        self.surface = Some(surface);
        self.device = Some(device);
        self.queue = Some(queue);
        self.surface_config = Some(surface_config);
    }

    fn window_event(
        &mut self,
        event_loop: &winit::event_loop::ActiveEventLoop,
        _window_id: winit::window::WindowId,
        event: WindowEvent,
    ) {
        if let Some(egui_winit) = &mut self.egui_winit {
            if let Some(window) = &self.window {
                let _ = egui_winit.on_window_event(window.as_ref(), &event);
            }
        }
        
        match event {
            WindowEvent::Resized(size) => {
                if let (Some(surface), Some(device), Some(config)) = 
                    (&self.surface, &self.device, &mut self.surface_config) {
                    config.width = size.width;
                    config.height = size.height;
                    surface.configure(device, config);
                }
            }
            WindowEvent::CloseRequested => {
                event_loop.exit();
            }
            WindowEvent::RedrawRequested => {
                self.render();
            }
            _ => {}
        }
    }

    fn about_to_wait(&mut self, _event_loop: &winit::event_loop::ActiveEventLoop) {
        if let Some(window) = &self.window {
            window.request_redraw();
        }
    }
}

impl AppState {
    fn render(&mut self) {
        let window = self.window.as_ref().unwrap();
        let egui_ctx = self.egui_ctx.as_ref().unwrap();
        let egui_winit = self.egui_winit.as_mut().unwrap();
        let egui_renderer = self.egui_renderer.as_mut().unwrap();
        let surface = self.surface.as_ref().unwrap();
        let device = self.device.as_ref().unwrap();
        let queue = self.queue.as_ref().unwrap();
        let surface_config = self.surface_config.as_ref().unwrap();
        
        let raw_input = egui_winit.take_egui_input(window.as_ref());
        let full_output = egui_ctx.run(raw_input, |ctx| {
            egui::CentralPanel::default().show(ctx, |ui| {
                ui.heading("Hello from Rust!");
                ui.label("This is running natively on Android");
            });
        });
        
        egui_winit.handle_platform_output(window.as_ref(), full_output.platform_output);
        
        let tris = egui_ctx.tessellate(full_output.shapes, full_output.pixels_per_point);
        
        let frame = surface.get_current_texture().unwrap();
        let view = frame.texture.create_view(&wgpu::TextureViewDescriptor::default());
        
        let mut encoder = device.create_command_encoder(&wgpu::CommandEncoderDescriptor::default());
        
        let screen_descriptor = egui_wgpu::ScreenDescriptor {
            size_in_pixels: [surface_config.width, surface_config.height],
            pixels_per_point: window.scale_factor() as f32,
        };
        
        for (id, image_delta) in &full_output.textures_delta.set {
            egui_renderer.update_texture(device, queue, *id, image_delta);
        }
        
        egui_renderer.update_buffers(device, queue, &mut encoder, &tris, &screen_descriptor);

        {
            let render_pass = encoder.begin_render_pass(&wgpu::RenderPassDescriptor {
                label: Some("egui render pass"),
                color_attachments: &[Some(wgpu::RenderPassColorAttachment {
                    view: &view,
                    resolve_target: None,
                    ops: wgpu::Operations {
                        load: wgpu::LoadOp::Clear(wgpu::Color::BLACK),
                        store: wgpu::StoreOp::Store,
                    },
                })],
                depth_stencil_attachment: None,
                timestamp_writes: None,
                occlusion_query_set: None,
            });

            egui_renderer.render(&mut render_pass.forget_lifetime(), &tris, &screen_descriptor);
        }
        
        for id in &full_output.textures_delta.free {
            egui_renderer.free_texture(id);
        }
        
        queue.submit(Some(encoder.finish()));
        frame.present();
    }
}