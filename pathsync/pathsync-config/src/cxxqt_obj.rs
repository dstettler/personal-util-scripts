
#[cxx_qt::bridge]
mod qobj {
    unsafe extern "RustQt" {
        #[qobject]
        #[qml_element]
        type Hello = super::HelloRust;
    }

    unsafe extern "RustQt" {
        #[qinvokable]
        fn say_hello(self: &Hello);
    }
}

#[derive(Default)]
pub struct HelloRust {}

impl qobj::Hello {
    pub fn say_hello(&self) {
        println!("Hello world!")
    }
}