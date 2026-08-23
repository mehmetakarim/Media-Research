// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::process::Command;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchResponse {
    pub success: bool,
    pub platform: String,
    pub raw_output: String,
    pub error: Option<String>,
}

// Projenin tam disk kök dizini (sanal ortam ve scriptler burada bulunur)
const PROJECT_DIR: &str = "/Volumes/Mac Harici Disk/VibeProject/Agent-Reach";

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
async fn run_doctor() -> Result<String, String> {
    tauri::async_runtime::spawn_blocking(move || {
        let cmd = format!("cd \"{}\" && source venv/bin/activate && agent-reach doctor", PROJECT_DIR);
        let output = Command::new("bash")
            .arg("-c")
            .arg(&cmd)
            .output()
            .map_err(|e| format!("Doktor komutu çalıştırılamadı: {}", e))?;

        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();

        if output.status.success() {
            Ok(stdout)
        } else {
            Ok(format!("{}\n{}", stdout, stderr))
        }
    })
    .await
    .map_err(|e| format!("İş parçacığı yürütme hatası: {}", e))?
}

#[tauri::command]
async fn execute_search(platform: String, query: String, limit: Option<u32>) -> Result<SearchResponse, String> {
    tauri::async_runtime::spawn_blocking(move || {
        let lim = limit.unwrap_or(10);
        let python_bin = format!("{}/venv/bin/python3", PROJECT_DIR);
        let script = match platform.as_str() {
            "all" => format!("{}/agent_reach/tools/all_search.py", PROJECT_DIR),
            "youtube" => format!("{}/agent_reach/tools/yt_search.py", PROJECT_DIR),
            "instagram" => format!("{}/agent_reach/tools/ig_search.py", PROJECT_DIR),
            "pinterest" => format!("{}/agent_reach/tools/pin_search.py", PROJECT_DIR),
            "reddit" => format!("{}/agent_reach/tools/reddit_search.py", PROJECT_DIR),
            "github" => format!("{}/agent_reach/tools/github_search.py", PROJECT_DIR),
            "linkedin" => format!("{}/agent_reach/tools/linkedin_search.py", PROJECT_DIR),
            "tiktok" => format!("{}/agent_reach/tools/tiktok_search.py", PROJECT_DIR),
            "web" => format!("{}/agent_reach/tools/web_search.py", PROJECT_DIR),
            "x" | "twitter" | _ => format!("{}/agent_reach/tools/twitter_search.py", PROJECT_DIR),
        };

        let output = Command::new(&python_bin)
            .arg(&script)
            .arg(&query)
            .arg(lim.to_string())
            .current_dir(PROJECT_DIR)
            .env("PYTHONPATH", PROJECT_DIR)
            .env("PATH", "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin")
            .output()
            .map_err(|e| format!("Arama komutu tetiklenemedi: {}", e))?;

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
    })
    .await
    .map_err(|e| format!("İş parçacığı yürütme hatası: {}", e))?
}

#[tauri::command]
async fn fetch_url_content(url: String) -> Result<String, String> {
    tauri::async_runtime::spawn_blocking(move || {
        let cmd = format!("curl -s \"https://r.jina.ai/{}\"", url);
        let output = Command::new("bash")
            .arg("-c")
            .arg(&cmd)
            .output()
            .map_err(|e| format!("URL okuma hatası: {}", e))?;

        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();

        if output.status.success() && !stdout.trim().is_empty() {
            Ok(stdout)
        } else {
            Err(if !stderr.is_empty() { stderr } else { "İçerik boş döndü".to_string() })
        }
    })
    .await
    .map_err(|e| format!("İş parçacığı yürütme hatası: {}", e))?
}

#[tauri::command]
fn save_cookies(service: String, cookie_val: String) -> Result<String, String> {
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

    let cmd = format!(
        "cd \"{}\" && source venv/bin/activate && agent-reach configure {} \"{}\"",
        PROJECT_DIR,
        key,
        cookie_val.replace("\"", "\\\"")
    );

    let output = Command::new("bash")
        .arg("-c")
        .arg(&cmd)
        .output()
        .map_err(|e| format!("Çerez kaydetme hatası: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();

    if output.status.success() {
        Ok(stdout)
    } else {
        Err(format!("{}\n{}", stdout, stderr))
    }
}

fn call_gemini_with_fallback(prompt: &str, api_key: &str, primary_model: &str) -> Result<String, String> {
    let mut model_chain = vec![
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
fn extract_browser_cookies(browser: String) -> Result<String, String> {
    let script = format!(
        "cd \"{}\" && source venv/bin/activate && python3 -c \"import json; from agent_reach.cookie_extract import extract_all; print(json.dumps(extract_all('{}')))\"",
        PROJECT_DIR,
        browser.to_lowercase()
    );

    let output = Command::new("bash")
        .arg("-c")
        .arg(&script)
        .output()
        .map_err(|e| format!("Çerez okuyucu betiği çalıştırılamadı: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();

    if output.status.success() && !stdout.trim().is_empty() {
        Ok(stdout)
    } else {
        Err(format!("Tarayıcı çerezleri okunamadı: {}\n{}", stderr, stdout))
    }
}

#[tauri::command]
fn save_file_to_downloads(filename: String, base64_data: String) -> Result<String, String> {
    use std::fs;
    use std::io::Write;
    use std::path::PathBuf;
    use std::process::Stdio;

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

    // Safe writing using Python process with STDIN to avoid argument length limits
    let mut child = Command::new("python3")
        .arg("-c")
        .arg(format!("import sys, base64; open(r'{}', 'wb').write(base64.b64decode(sys.stdin.read().strip()))", file_path.to_string_lossy()))
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Python işlemi başlatılamadı: {}", e))?;

    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(clean_b64.as_bytes()).map_err(|e| format!("Veri yazılamadı: {}", e))?;
    }

    let output = child.wait_with_output().map_err(|e| format!("Dosya yazma işlemi tamamlanamadı: {}", e))?;

    if output.status.success() && file_path.exists() {
        Ok(file_path.to_string_lossy().to_string())
    } else {
        Err(format!("Dosya kaydedilemedi: {}", String::from_utf8_lossy(&output.stderr)))
    }
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
