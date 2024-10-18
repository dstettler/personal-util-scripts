// use std::{collections::HashMap, env, fs::File, os::windows};

pub mod cxxqt_obj;

use cxx_qt_lib::{QGuiApplication, QQmlApplicationEngine, QUrl};

mod configurator;

fn main() {
    // Create the application and engine
    let mut app = QGuiApplication::new();
    let mut engine = QQmlApplicationEngine::new();

    // Load the QML path into the engine
    if let Some(engine) = engine.as_mut() {
        engine.load(&QUrl::from("qrc:/qt/qml/me/dstet/pathsync/config/qml/main.qml"));
    }

    // Start the app
    if let Some(app) = app.as_mut() {
        app.exec();
    }

    // // Manual argument parsing to avoid adding too many crates
    // let args: Vec<String> = env::args().collect();

    // let mut m: HashMap<String, String> = HashMap::new();
    // for i in (2..args.len() - 1).step_by(2) {
    //     m.insert(args[i].clone(), args[i+1].clone());
    // }

    // let mut s = configurator::init_syncfile();
    // s.st_pairs = m;
    
    // let f = File::create(args[1].as_str()).unwrap();

    // configurator::write_syncfile(f, &mut s);
}