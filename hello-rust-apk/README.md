```bash
sudo apt install openjdk-17-jdk

# Verify
java -version

# maybe not needed
# Set JAVA_HOME
# export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
# export PATH=$PATH:$JAVA_HOME/bin


rustup target add aarch64-linux-android

cd ~
mkdir android-sdk 
cd android-sdk

wget https://dl.google.com/android/repository/android-ndk-r26d-linux.zip
unzip android-ndk-r26d-linux.zip
export NDK_HOME=$HOME/android-sdk/android-ndk-r26d

wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip commandlinetools-linux-11076708_latest.zip



# Create the proper structure
mkdir -p cmdline-tools/latest

# Move the contents INTO latest/
mv cmdline-tools/bin cmdline-tools/lib cmdline-tools/NOTICE.txt cmdline-tools/source.properties cmdline-tools/latest/

# Now try again
./cmdline-tools/latest/bin/sdkmanager --sdk_root=$HOME/android-sdk "build-tools;34.0.0" "platform-tools" "platforms;android-34"


# Download command line tools from:
# https://developer.android.com/studio#command-line-tools-only
# Extract and install build-tools:
# ./cmdline-tools/latest/bin/sdkmanager "build-tools;34.0.0" "platform-tools" "platforms;android-34"

export ANDROID_HOME=$HOME/android-sdk


cargo install cargo-apk

cd without-objective/hello-rust-apk

cargo new --lib hello_android
cd hello_android
```


```toml
[package]
name = "hello_android"
version = "0.1.0"
edition = "2024"

[lib]
crate-type = ["cdylib"]

[dependencies]
android-activity = { version = "0.6", features = ["native-activity"] }

[package.metadata.android]
package = "com.example.hello_android"
build_targets = ["aarch64-linux-android"]

[package.metadata.android.sdk]
min_sdk_version = 28
target_sdk_version = 34
```


```rust # lib.rs
use android_activity::{AndroidApp, MainEvent, PollEvent};

#[no_mangle]
fn android_main(app: AndroidApp) {
    // Event loop
    loop {
        app.poll_events(Some(std::time::Duration::from_millis(100)), |event| {
            match event {
                PollEvent::Main(MainEvent::Destroy) => {
                    // App closing
                },
                _ => {}
            }
        });
        
        // Your logic here
        // For now, just loops - add actual UI rendering later
    }
}
```


```bash
cargo apk build 
# APK will be in: target/debug/apk/hello_android.apk

# cargo apk build --release
# APK will be in: target/release/apk/hello_android.apk
```




---


Sources:
- https://github.com/matthewjberger/wgpu-example - Minimal example of Rust, wgpu, and egui for multiple platforms including Android
- https://github.com/inferrna/hello_world_android_egui - Egui + winit + wgpu Android example

---

Look into: fredrik-hammar egui android demo