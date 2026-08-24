// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::process::Command;
use std::path::{Path, PathBuf};
use serde::{Deserialize, Serialize};
use tauri::Manager;

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchResponse {
    pub success: bool,
    pub platform: String,
    pub raw_output: String,
    pub error: Option<String>,
}

// Projenin yerel geliştirme disk kök dizini (Mac geliştirme ortamı)
const DEV_PROJECT_DIR: &str = "/Volumes/Mac Harici Disk/VibeProject/Agent-Reach";

fn resolve_project_root(app: &tauri::AppHandle) -> PathBuf {
    // 1. Geliştirme ortamı yolu kontrolü (Mac hard drive)
    let dev_root = Path::new(DEV_PROJECT_DIR);
    if dev_root.join("agent_reach").exists() {
        return dev_root.to_path_buf();
    }

    // 2. Tauri bundle kaynak dizini kontrolü (macOS .app Resources veya Windows resources)
    if let Ok(res_dir) = app.path().resource_dir() {
        if res_dir.join("agent_reach").exists() {
            return res_dir;
        }
        if res_dir.join("_up_").join("agent_reach").exists() {
            return res_dir.join("_up_");
        }
    }

    // 3. Çalıştırılabilir ikili dosya (exe) yanındaki dizin kontrolü
    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            if parent.join("agent_reach").exists() {
                return parent.to_path_buf();
            }
            if parent.join("resources").join("agent_reach").exists() {
                return parent.join("resources");
            }
            if parent.join("resources").join("_up_").join("agent_reach").exists() {
                return parent.join("resources").join("_up_");
            }
        }
    }

    PathBuf::from(".")
}

fn resolve_python_bin(root: &Path) -> String {
    #[cfg(target_os = "windows")]
    {
        let venv_py = root.join("venv").join("Scripts").join("python.exe");
        if venv_py.exists() {
            return venv_py.to_string_lossy().to_string();
        }
        // Windows standart python komutu
        "python".to_string()
    }
    #[cfg(not(target_os = "windows"))]
    {
        let venv_py = root.join("venv").join("bin").join("python3");
        if venv_py.exists() {
            return venv_py.to_string_lossy().to_string();
        }
        "python3".to_string()
    }
}

#[tauri::command]
fn open_external_url(url: String) -> Result<(), String> {
    #[cfg(target_os = "macos")]
    {
        Command::new("open")
            .arg(&url)
            .spawn()
            .map_err(|e| format!("URL açılamadı: {}", e))?;
    }
    #[cfg(target_os = "windows")]
    {
        Command::new("cmd")
            .args(["/C", "start", &url])
            .spawn()
            .map_err(|e| format!("URL açılamadı: {}", e))?;
    }
    #[cfg(target_os = "linux")]
    {
        Command::new("xdg-open")
            .arg(&url)
            .spawn()
            .map_err(|e| format!("URL açılamadı: {}", e))?;
    }
    Ok(())
}

#[tauri::command]
fn run_doctor(app: tauri::AppHandle) -> Result<String, String> {
    let root = resolve_project_root(&app);
    let python_bin = resolve_python_bin(&root);

    let mut cmd = Command::new(&python_bin);
    cmd.arg("-m")
       .arg("agent_reach.cli")
       .arg("doctor")
       .current_dir(&root)
       .env("PYTHONPATH", &root);

    let output = cmd.output().map_err(|e| format!("Doktor komutu çalıştırılamadı (Python: {}): {}", python_bin, e))?;

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();

    if output.status.success() {
        Ok(stdout)
    } else {
        Ok(format!("{}\n{}", stdout, stderr))
    }
}

#[tauri::command]
fn execute_search(app: tauri::AppHandle, platform: String, query: String, limit: Option<u32>) -> Result<SearchResponse, String> {
    let lim = limit.unwrap_or(10);
    let root = resolve_project_root(&app);
    let python_bin = resolve_python_bin(&root);

    let script_file = match platform.as_str() {
        "all" => "all_search.py",
        "youtube" => "yt_search.py",
        "instagram" => "ig_search.py",
        "pinterest" => "pin_search.py",
        "reddit" => "reddit_search.py",
        "github" => "github_search.py",
        "linkedin" => "linkedin_search.py",
        "tiktok" => "tiktok_search.py",
        "web" => "web_search.py",
        "x" | "twitter" | _ => "twitter_search.py",
    };

    let script_path = root.join("agent_reach").join("tools").join(script_file);

    let sys_path = std::env::var("PATH").unwrap_or_default();
    let home = std::env::var("HOME").or_else(|_| std::env::var("USERPROFILE")).unwrap_or_default();
    
    #[cfg(target_os = "windows")]
    let full_path = format!("{};{}\\.local\\bin;{}", sys_path, home, sys_path);
    
    #[cfg(not(target_os = "windows"))]
    let full_path = format!("{}:{}/.nvm/versions/node/v20.19.5/bin:{}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin", sys_path, home, home);

    let mut cmd = Command::new(&python_bin);
    cmd.arg(&script_path)
       .arg(&query)
       .arg(lim.to_string())
       .current_dir(&root)
       .env("PYTHONPATH", &root)
       .env("PATH", full_path);

    let output = cmd.output().map_err(|e| format!("Arama komutu tetiklenemedi (Python: {}, Script: {:?}): {}", python_bin, script_path, e))?;

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();

    if output.status.success() {
        Ok(SearchResponse {
            success: true,
            platform,
            raw_output: stdout,
            error: None,
        })
    } else {
        let err_msg = if !stderr.trim().is_empty() {
            stderr
        } else if !stdout.trim().is_empty() {
            stdout.clone()
        } else {
            "Arama komutu sıfır dışı çıkış kodu döndürdü.".to_string()
        };

        Ok(SearchResponse {
            success: false,
            platform,
            raw_output: stdout,
            error: Some(err_msg),
        })
    }
}

#[tauri::command]
fn fetch_url_content(url: String) -> Result<String, String> {
    let target = format!("https://r.jina.ai/{}", url);
    let client_res = Command::new("curl")
        .arg("-s")
        .arg(&target)
        .output()
        .map_err(|e| format!("URL okuma hatası: {}", e))?;

    let stdout = String::from_utf8_lossy(&client_res.stdout).to_string();
    let stderr = String::from_utf8_lossy(&client_res.stderr).to_string();

    if client_res.status.success() && !stdout.trim().is_empty() {
        Ok(stdout)
    } else {
        Err(if !stderr.is_empty() { stderr } else { "İçerik boş döndü".to_string() })
    }
}

#[tauri::command]
fn save_cookies(app: tauri::AppHandle, service: String, cookie_val: String) -> Result<String, String> {
    let key = match service.as_str() {
        "twitter" | "x" => "twitter-cookies",
        "instagram" => "instagram-cookies",
        "pinterest" => "pinterest-cookies",
        "reddit" => "reddit-cookies",
        "linkedin" => "linkedin-cookies",
        "tiktok" => "tiktok-cookies",
        "github" => "github-token",
        "youtube" => "youtube-cookies",
        "xhs" => "xhs-cookies",
        "xiaoyuzhou" => "groq-key",
        _ => "twitter-cookies",
    };

    let root = resolve_project_root(&app);
    let python_bin = resolve_python_bin(&root);

    let mut cmd = Command::new(&python_bin);
    cmd.arg("-m")
       .arg("agent_reach.cli")
       .arg("configure")
       .arg(key)
       .arg(&cookie_val)
       .current_dir(&root)
       .env("PYTHONPATH", &root);

    let output = cmd.output().map_err(|e| format!("Çerez kaydetme hatası: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();

    if output.status.success() {
        Ok(stdout)
    } else {
        Err(format!("{}\n{}", stdout, stderr))
    }
}

fn call_gemini_with_fallback(prompt: &str, api_key: &str, primary_model: &str) -> Result<String, String> {
    let model_chain = vec![
        primary_model.to_string(),
        "gemini-3.7-flash".to_string(),
        "gemini-3.5-flash".to_string(),
        "gemini-2.5-flash".to_string(),
        "gemini-3.5-flash-lite".to_string(),
        "gemini-2.5-flash-lite".to_string(),
        "gemma-4-31b-it".to_string(),
    ];
    // Remove duplicates while preserving order
    let mut unique_chain = Vec::new();
    for m in model_chain {
        let clean = m.trim().replace("models/", "");
        if !clean.is_empty() && !unique_chain.contains(&clean) {
            unique_chain.push(clean);
        }
    }

    let body = serde_json::json!({
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    });

    let mut last_error = String::new();

    for m in &unique_chain {
        let url = format!(
            "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}",
            m,
            api_key
        );

        let client_res = Command::new("curl")
            .arg("-s")
            .arg("-X")
            .arg("POST")
            .arg(&url)
            .arg("-H")
            .arg("Content-Type: application/json; charset=utf-8")
            .arg("--data-binary")
            .arg(body.to_string())
            .output();

        match client_res {
            Ok(output) => {
                let res_str = String::from_utf8_lossy(&output.stdout).to_string();
                if let Ok(parsed) = serde_json::from_str::<serde_json::Value>(&res_str) {
                    if let Some(err) = parsed.get("error") {
                        let err_msg = err.get("message").and_then(|v| v.as_str()).unwrap_or("Hata");
                        last_error = err_msg.to_string();
                        // If quota / rate limit / high demand, continue to next model in chain
                        if err_msg.contains("high demand") || err_msg.contains("quota") || err_msg.contains("RESOURCE_EXHAUSTED") || err_msg.contains("429") {
                            continue;
                        }
                    } else if parsed.get("candidates").is_some() {
                        return Ok(res_str);
                    }
                }
            }
            Err(e) => {
                last_error = format!("Curl hatası: {}", e);
            }
        }
    }

    if last_error.is_empty() {
        last_error = "Tüm modeller denendi ancak yanıt alınamadı.".to_string();
    }
    Err(last_error)
}

#[tauri::command]
fn generate_ai_summary(prompt: String, api_key: Option<String>, model: Option<String>) -> Result<String, String> {
    let key = match api_key {
        Some(k) if !k.trim().is_empty() => k.trim().to_string(),
        _ => "GEMINI_API_KEY_ENV".to_string(),
    };

    let primary = model.unwrap_or_else(|| "gemini-2.5-flash".to_string());
    call_gemini_with_fallback(&prompt, &key, &primary)
}

#[tauri::command]
fn fetch_gemini_models(api_key: Option<String>) -> Result<String, String> {
    let key = match api_key {
        Some(k) if !k.trim().is_empty() => k.trim().to_string(),
        _ => "GEMINI_API_KEY_ENV".to_string(),
    };

    let url = format!("https://generativelanguage.googleapis.com/v1beta/models?key={}", key);
    let client_res = Command::new("curl")
        .arg("-s")
        .arg(url)
        .output()
        .map_err(|e| format!("Model listesi alınamadı: {}", e))?;

    let res_str = String::from_utf8_lossy(&client_res.stdout).to_string();
    Ok(res_str)
}

#[tauri::command]
fn translate_text(text: String, api_key: Option<String>, model: Option<String>) -> Result<String, String> {
    let key = match api_key {
        Some(k) if !k.trim().is_empty() => k.trim().to_string(),
        _ => "GEMINI_API_KEY_ENV".to_string(),
    };

    let prompt = format!(
        "Lütfen aşağıdaki metni anlam bütünlüğünü, terimleri ve varsa sosyal medya havasını (emoji, mention, hashtag) koruyarak akıcı ve doğal bir Türkçeye çevir. Sadece çeviriyi ver, ek açıklama yapma:\n\n{}",
        text
    );

    let primary = model.unwrap_or_else(|| "gemini-2.5-flash".to_string());
    call_gemini_with_fallback(&prompt, &key, &primary)
}

#[tauri::command]
fn extract_browser_cookies(app: tauri::AppHandle, browser: String) -> Result<String, String> {
    let root = resolve_project_root(&app);
    let python_bin = resolve_python_bin(&root);

    let code = format!(
        "import json; from agent_reach.cookie_extract import extract_all; print(json.dumps(extract_all('{}')))",
        browser.to_lowercase()
    );

    let mut cmd = Command::new(&python_bin);
    cmd.arg("-c")
       .arg(&code)
       .current_dir(&root)
       .env("PYTHONPATH", &root);

    let output = cmd.output().map_err(|e| format!("Çerez okuyucu betiği çalıştırılamadı (Python: {}): {}", python_bin, e))?;

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();

    if output.status.success() && !stdout.trim().is_empty() {
        Ok(stdout)
    } else {
        Err(format!("Tarayıcı çerezleri okunamadı: {}\n{}", stderr, stdout))
    }
}

fn decode_base64_bytes(input: &str) -> Vec<u8> {
    let table = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut decode_map = [255u8; 256];
    for (i, &c) in table.iter().enumerate() {
        decode_map[c as usize] = i as u8;
    }
    let clean: String = input.chars().filter(|c| !c.is_whitespace()).collect();
    let mut bytes = Vec::with_capacity(clean.len() * 3 / 4);
    let mut buf = 0u32;
    let mut bits = 0;
    for &b in clean.as_bytes() {
        if b == b'=' { break; }
        let val = decode_map[b as usize];
        if val == 255 { continue; }
        buf = (buf << 6) | (val as u32);
        bits += 6;
        if bits >= 8 {
            bits -= 8;
            bytes.push((buf >> bits) as u8);
        }
    }
    bytes
}

#[tauri::command]
fn save_file_to_downloads(filename: String, base64_data: String) -> Result<String, String> {
    use std::fs;

    let home_dir = std::env::var("HOME").or_else(|_| std::env::var("USERPROFILE")).map_err(|_| "Ev dizini bulunamadı".to_string())?;
    let downloads_dir = PathBuf::from(home_dir).join("Downloads");
    
    if !downloads_dir.exists() {
        let _ = fs::create_dir_all(&downloads_dir);
    }

    let file_path = downloads_dir.join(&filename);
    
    let clean_b64 = if let Some(idx) = base64_data.find(",") {
        &base64_data[idx + 1..]
    } else {
        &base64_data
    };

    let decoded_bytes = decode_base64_bytes(clean_b64);
    fs::write(&file_path, &decoded_bytes).map_err(|e| format!("Dosya kaydedilemedi: {}", e))?;

    Ok(file_path.to_string_lossy().to_string())
}

#[tauri::command]
fn show_in_folder(path: String) -> Result<(), String> {
    #[cfg(target_os = "macos")]
    {
        Command::new("open")
            .arg("-R")
            .arg(&path)
            .spawn()
            .map_err(|e| format!("Klasör açılamadı: {}", e))?;
    }
    #[cfg(target_os = "windows")]
    {
        Command::new("explorer")
            .arg(format!("/select,{}", path))
            .spawn()
            .map_err(|e| format!("Klasör açılamadı: {}", e))?;
    }
    #[cfg(target_os = "linux")]
    {
        Command::new("xdg-open")
            .arg(&path)
            .spawn()
            .map_err(|e| format!("Klasör açılamadı: {}", e))?;
    }
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            open_external_url,
            run_doctor,
            execute_search,
            fetch_url_content,
            save_cookies,
            generate_ai_summary,
            fetch_gemini_models,
            translate_text,
            extract_browser_cookies,
            save_file_to_downloads,
            show_in_folder
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
