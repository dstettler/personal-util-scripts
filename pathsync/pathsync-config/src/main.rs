use iced::{Alignment, Element, Length, Settings};
use iced::widget::{button, pick_list, row, text, text_input, Button, Column, Container, Row, Text, TextInput};
use serde::de::IntoDeserializer;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::{env, fs};
use std::process::Command;
use rfd::FileDialog;

const PROGRAM_TITLE: &str = "Pathsync Configurator";
const PATHSYNC_EXECUTABLE_BASE: &str = "gpathsync";

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SyncPair {
    src: String,
    target: String,
    cache: Option<String>,
    ignore: Option<Vec<String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
struct Config {
    pairs: Vec<SyncPair>,
    ignore: Vec<String>,
}

#[derive(Default)]
struct ConfigEditor {
    config: Config,
    add_button: bool,
    save_button: bool,
    load_button: bool,
    run_button: bool,
    src_value: String,
    target_value: String,
    ignore_value: String,
    global_ignore_value: String,
    config_file: Option<String>,
    selected_pair: Option<usize>,
}

#[derive(Debug, Clone)]
enum Message {
    SrcChanged(String),
    TargetChanged(String),
    IgnoreChanged(String),
    GlobalIgnoreChanged(String),
    AddPair,
    RemovePair(usize),
    EditPair(usize),
    SaveConfig,
    LoadConfig,
    RunSync,
    FilePicked(Option<String>),
}

impl ConfigEditor {
    fn update(&mut self, message: Message) {
        match message {
            Message::SrcChanged(value) => self.src_value = value,
            Message::TargetChanged(value) => self.target_value = value,
            Message::IgnoreChanged(value) => self.ignore_value = value,
            Message::GlobalIgnoreChanged(value) => self.global_ignore_value = value,
            Message::AddPair => {
                if !self.src_value.is_empty() && !self.target_value.is_empty() {
                    let ignore_list = if self.ignore_value.is_empty() {
                        None
                    } else {
                        Some(self.ignore_value.split(',').map(|s| s.trim().to_string()).collect())
                    };
                    self.config.pairs.push(SyncPair {
                        src: self.src_value.clone(),
                        target: self.target_value.clone(),
                        cache: None,
                        ignore: ignore_list,
                    });
                }
            }
            Message::RemovePair(index) => {
                if index < self.config.pairs.len() {
                    self.config.pairs.remove(index);
                }
            }
            Message::EditPair(index) => {
                if let Some(pair) = self.config.pairs.get(index) {
                    self.src_value = pair.src.clone();
                    self.target_value = pair.target.clone();
                    self.ignore_value = pair.ignore.clone().unwrap_or_default().join(", ");
                    self.selected_pair = Some(index);
                }
            }
            Message::SaveConfig => {
                if let Some(ref file) = self.config_file {
                    self.config.ignore = self.global_ignore_value
                        .split(',')
                        .map(|s| s.trim().to_string())
                        .collect();
                    fs::write(file, serde_yml::to_string(&self.config).unwrap()).unwrap();
                }
            }
            Message::LoadConfig => {
                let path = FileDialog::new().pick_file().map(|p| p.to_string_lossy().into_owned());
                self.update(Message::FilePicked(path));
            }
            Message::RunSync => {
                // Get current executable directory and run gpathsync in same dir (will fail if running from symlink)
                if let Some(ref file) = self.config_file {                    
                    let executable = env::current_exe().unwrap();
                    if let Some(exe_parent) = executable.parent() {
                        let executable_name: String;
                        if cfg!(windows) {
                            // Windows will always append a .exe to an executable binary
                            executable_name = format!("{}.exe", PATHSYNC_EXECUTABLE_BASE);
                        } else {
                            executable_name = format!("{}", PATHSYNC_EXECUTABLE_BASE);
                        }

                        let mut target_path = PathBuf::from(exe_parent);
                        target_path.push(executable_name);

                        let _ = Command::new(format!("{}", target_path.display()))
                                .arg("-r")
                                .arg("-s")
                                .arg(file)
                                .spawn();
                        println!("{}", target_path.display())
                    }
                }
            }
            Message::FilePicked(Some(path)) => {
                if let Ok(contents) = fs::read_to_string(&path) {
                    if let Ok(config) = serde_yml::from_str(&contents) {
                        self.config = config;
                        self.config_file = Some(path);
                        self.global_ignore_value = self.config.ignore.clone().join(", ")
                    }
                }
            }
            Message::FilePicked(None) => {}
        }
    }

    fn view(&self) -> Element<Message> {
        let pairs: Element<_> = self.config.pairs.iter().enumerate().fold(Column::new().spacing(10), |column, (index, pair)| {
            column.push(
                row![
                text!("{} -> {}", pair.src, pair.target),
                button("Edit").on_press(Message::EditPair(index)),
                button("Remove").on_press(Message::RemovePair(index))
                ].spacing(10)
            )
        }).into();
        
        let load_btn = button("Load Config").on_press(Message::LoadConfig);
        let add_btn = button("Add Pair").on_press(Message::AddPair);
        let save_btn = button("Save Config").on_press(Message::SaveConfig);
        let run_btn = button("Run Utility").on_press(Message::RunSync);

        let src_input_field = text_input("Source Path", &self.src_value).on_input(Message::SrcChanged);
        let target_input_field = text_input("Target Path", &self.target_value).on_input(Message::TargetChanged);
        let pair_ignore_input_field = text_input("Ignores (comma-separated)", &self.ignore_value).on_input(Message::IgnoreChanged);
        let global_ignore_input_field = text_input("Global Ignores (comma-separated)", &self.global_ignore_value).on_input(Message::GlobalIgnoreChanged);

        let content = iced::widget::column![
            text!("{}", PROGRAM_TITLE),
            load_btn,
            src_input_field,
            target_input_field,
            pair_ignore_input_field,
            add_btn,
            text!("Global Ignore Rules"),
            global_ignore_input_field,
            save_btn,
            run_btn,
            pairs].spacing(10).into();
        
        content
    }
}

fn main() -> iced::Result {
    iced::run(PROGRAM_TITLE, ConfigEditor::update, ConfigEditor::view)
}
