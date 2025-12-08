use android_activity::AndroidApp;
use winit::event_loop::EventLoop;
use winit::application::ApplicationHandler;
use winit::event::WindowEvent;
use winit::window::Window;
use egui_wgpu::wgpu;
use std::sync::Arc;
use std::collections::VecDeque;
use crossbeam_channel::{Receiver, unbounded};
use std::thread;
use std::time::SystemTime;

fn setup_foreground_notification(app: &AndroidApp) {
    use jni::objects::{JObject, JValue};
    use jni::sys::jint;

    let vm = unsafe { jni::JavaVM::from_raw(app.vm_as_ptr() as *mut _) }.unwrap();
    let mut env = vm.attach_current_thread().unwrap();
    let activity = unsafe { JObject::from_raw(app.activity_as_ptr() as *mut _) };

    // Create notification channel (required for Android 8.0+)
    let channel_id = env.new_string("file_monitor_channel").unwrap();
    let channel_name = env.new_string("File Monitor Service").unwrap();
    let importance = 3; // IMPORTANCE_DEFAULT

    // Get NotificationManager
    let notification_service = env.new_string("notification").unwrap();
    let notification_manager = env.call_method(
        &activity,
        "getSystemService",
        "(Ljava/lang/String;)Ljava/lang/Object;",
        &[JValue::Object(&notification_service)],
    ).unwrap().l().unwrap();

    // Create NotificationChannel for Android O+
    if let Ok(channel_class) = env.find_class("android/app/NotificationChannel") {
        let channel = env.new_object(
            channel_class,
            "(Ljava/lang/String;Ljava/lang/CharSequence;I)V",
            &[
                JValue::Object(&channel_id),
                JValue::Object(&channel_name),
                JValue::Int(importance),
            ],
        ).unwrap();

        let _ = env.call_method(
            &notification_manager,
            "createNotificationChannel",
            "(Landroid/app/NotificationChannel;)V",
            &[JValue::Object(&channel)],
        );
    }

    // Build notification
    let builder_class = env.find_class("android/app/Notification$Builder").unwrap();
    let builder = if env.find_class("android/app/NotificationChannel").is_ok() {
        // Android O+ requires channel ID
        env.new_object(
            builder_class,
            "(Landroid/content/Context;Ljava/lang/String;)V",
            &[JValue::Object(&activity), JValue::Object(&channel_id)],
        ).unwrap()
    } else {
        env.new_object(
            builder_class,
            "(Landroid/content/Context;)V",
            &[JValue::Object(&activity)],
        ).unwrap()
    };

    let title = env.new_string("Picture Monitor Active").unwrap();
    let text = env.new_string("Monitoring Pictures directory for changes").unwrap();

    let _ = env.call_method(
        &builder,
        "setContentTitle",
        "(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;",
        &[JValue::Object(&title)],
    );

    let _ = env.call_method(
        &builder,
        "setContentText",
        "(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;",
        &[JValue::Object(&text)],
    );

    // Set small icon (use default Android icon)
    let icon_id: jint = 0x01080078; // android.R.drawable.ic_dialog_info
    let _ = env.call_method(
        &builder,
        "setSmallIcon",
        "(I)Landroid/app/Notification$Builder;",
        &[JValue::Int(icon_id)],
    );

    let notification = env.call_method(
        &builder,
        "build",
        "()Landroid/app/Notification;",
        &[],
    ).unwrap().l().unwrap();

    // Show notification
    let notification_id: jint = 1;
    let _ = env.call_method(
        &notification_manager,
        "notify",
        "(ILandroid/app/Notification;)V",
        &[JValue::Int(notification_id), JValue::Object(&notification)],
    );
}

#[derive(Clone, Debug)]
struct FileEvent {
    event_type: String,
    path: String,
    timestamp: SystemTime,
}

fn start_file_monitor() -> Receiver<FileEvent> {
    let (sender, receiver) = unbounded();

    thread::spawn(move || {
        // Get the Pictures directory path
        // On Android, this is typically /storage/emulated/0/Pictures
        let pictures_path = std::path::Path::new("/storage/emulated/0/Pictures");

        if !pictures_path.exists() {
            eprintln!("Pictures directory does not exist");
            return;
        }

        // Set up inotify to watch the Pictures directory recursively
        match inotify::Inotify::init() {
            Ok(mut inotify) => {
                // Add watch for the Pictures directory
                if let Err(e) = inotify.watches().add(
                    pictures_path,
                    inotify::WatchMask::CREATE | inotify::WatchMask::DELETE
                ) {
                    eprintln!("Failed to add inotify watch: {}", e);
                    return;
                }

                // Also watch subdirectories
                if let Ok(entries) = std::fs::read_dir(pictures_path) {
                    for entry in entries.flatten() {
                        if let Ok(metadata) = entry.metadata() {
                            if metadata.is_dir() {
                                let _ = inotify.watches().add(
                                    entry.path(),
                                    inotify::WatchMask::CREATE | inotify::WatchMask::DELETE
                                );
                            }
                        }
                    }
                }

                let mut buffer = [0u8; 4096];
                loop {
                    match inotify.read_events_blocking(&mut buffer) {
                        Ok(events) => {
                            for event in events {
                                let event_type = if event.mask.contains(inotify::EventMask::CREATE) {
                                    "Created"
                                } else if event.mask.contains(inotify::EventMask::DELETE) {
                                    "Deleted"
                                } else {
                                    "Unknown"
                                };

                                let path = event.name
                                    .map(|n| n.to_string_lossy().to_string())
                                    .unwrap_or_else(|| "unknown".to_string());

                                let file_event = FileEvent {
                                    event_type: event_type.to_string(),
                                    path,
                                    timestamp: SystemTime::now(),
                                };

                                if sender.send(file_event).is_err() {
                                    break;
                                }
                            }
                        }
                        Err(e) => {
                            eprintln!("Error reading inotify events: {}", e);
                            break;
                        }
                    }
                }
            }
            Err(e) => {
                eprintln!("Failed to initialize inotify: {}", e);
            }
        }
    });

    receiver
}

#[unsafe(no_mangle)]
fn android_main(app: AndroidApp) {
    use winit::platform::android::EventLoopBuilderExtAndroid;

    // Set up foreground notification to show we're running
    setup_foreground_notification(&app);

    let event_loop = EventLoop::builder()
        .with_android_app(app)
        .build()
        .unwrap();

    let file_event_receiver = start_file_monitor();
    let mut app_state = AppState::new(file_event_receiver);
    event_loop.run_app(&mut app_state).unwrap();
}

const MAX_EVENTS: usize = 100;

struct AppState {
    window: Option<Arc<Window>>,
    egui_ctx: Option<egui::Context>,
    egui_winit: Option<egui_winit::State>,
    egui_renderer: Option<egui_wgpu::Renderer>,
    surface: Option<wgpu::Surface<'static>>,
    device: Option<wgpu::Device>,
    queue: Option<wgpu::Queue>,
    surface_config: Option<wgpu::SurfaceConfiguration>,
    file_event_receiver: Receiver<FileEvent>,
    file_events: VecDeque<FileEvent>,
}

impl AppState {
    fn new(file_event_receiver: Receiver<FileEvent>) -> Self {
        Self {
            window: None,
            egui_ctx: None,
            egui_winit: None,
            egui_renderer: None,
            surface: None,
            device: None,
            queue: None,
            surface_config: None,
            file_event_receiver,
            file_events: VecDeque::new(),
        }
    }

    fn process_file_events(&mut self) {
        while let Ok(event) = self.file_event_receiver.try_recv() {
            self.file_events.push_front(event);
            if self.file_events.len() > MAX_EVENTS {
                self.file_events.pop_back();
            }
        }
    }
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
        self.process_file_events();
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
                ui.heading("📁 Picture Directory Monitor");
                ui.separator();

                ui.horizontal(|ui| {
                    ui.label("Status:");
                    ui.colored_label(egui::Color32::GREEN, "● Active");
                });

                ui.label(format!("Watching: /storage/emulated/0/Pictures"));
                ui.label(format!("Total events captured: {}", self.file_events.len()));

                ui.separator();
                ui.heading("Event Log");

                egui::ScrollArea::vertical()
                    .auto_shrink([false, false])
                    .stick_to_bottom(true)
                    .show(ui, |ui| {
                        if self.file_events.is_empty() {
                            ui.label("No events yet. Try taking a photo or managing files in your Pictures folder!");
                        } else {
                            for event in &self.file_events {
                                let time_str = format!("{:?}", event.timestamp);
                                let color = match event.event_type.as_str() {
                                    "Created" => egui::Color32::GREEN,
                                    "Deleted" => egui::Color32::RED,
                                    _ => egui::Color32::GRAY,
                                };

                                ui.horizontal(|ui| {
                                    ui.colored_label(color, &event.event_type);
                                    ui.label(&event.path);
                                });
                                ui.label(egui::RichText::new(&time_str).small().weak());
                                ui.separator();
                            }
                        }
                    });

                ui.separator();
                ui.small("💪 Native Android power! PWAs can't do this!");
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