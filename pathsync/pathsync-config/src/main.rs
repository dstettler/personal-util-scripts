use std::{collections::HashMap, env, fs::File};

mod configurator;

fn main() {
    let args: Vec<String> = env::args().collect();

    let mut m: HashMap<String, String> = HashMap::new();
    for i in (2..args.len() - 1).step_by(2) {
        m.insert(args[i].clone(), args[i+1].clone());
    }

    let mut s = configurator::init_syncfile();
    s.st_pairs = m;
    
    let f = File::create(args[1].as_str()).unwrap();

    configurator::write_syncfile(f, &mut s);
}