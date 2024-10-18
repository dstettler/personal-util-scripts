// use core::sync;
use std::{collections::HashMap, error::Error, fs::{self, create_dir_all, File}, path::Path, result::Result};

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct Syncfile {
    pub st_pairs: HashMap<String, String>,
    pub cache_dirs: HashMap<String, String>,
    pub ignore: Vec<String>
}

pub fn read_syncfile(file_reader: File) -> Result<Syncfile, Box<dyn Error>> {
    let f: Syncfile = serde_json::from_reader(file_reader)?;
    
    Ok(f)
}

pub fn write_syncfile(file_writer: File, syncfile: &mut Syncfile) -> Result<(), Box<dyn Error>> {
    for (key, val) in syncfile.st_pairs.iter() {
        if syncfile.cache_dirs.keys().find(|x| x == &key).unwrap_or(&"EMPTY".to_owned()) == "EMPTY" {
            syncfile.cache_dirs.insert(key.clone(), format!("{}/cache", val));
        }
    }

    for val in syncfile.st_pairs.values() {
        let val_path = Path::new(val.as_str());
        if !val_path.exists() {
            create_dir_all(val_path)?;
        }
    }

    for val in syncfile.cache_dirs.values() {
        let val_path = Path::new(val.as_str());

        if !val_path.exists() {
            println!("Creating: {}", val_path.as_os_str().to_str().unwrap());
            fs::write(val_path, "{}");
        }
    }
    
    Ok(serde_json::to_writer(file_writer, syncfile)?)
}

pub fn init_syncfile() -> Syncfile {
    Syncfile {
        st_pairs: HashMap::new(),
        cache_dirs: HashMap::new(),
        ignore: Vec::new()
    }
}