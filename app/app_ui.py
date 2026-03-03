import gradio as gr
from app_logic import chat_logic, reset_all

# =========================
# CSS THEME (TỐI & HÀI HÒA)
# =========================
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root { 
    /* MÀU NỀN VÀ KHUNG CHÍNH */
    --bg-main: #111827;
    --bg-surface: #1f2937;
    --bg-input: #374151;

    /* MÀU CHỮ */
    --text-main: #f3f4f6;
    --text-sub: #9ca3af;
    --text-inverse: #1f2937;

    /* MÀU VIỀN VÀ ĐIỂM NHẤN */
    --border-color: #374151;
    --accent: #2dd4bf;
    --accent-hover: #14b8a6;
    --accent-sub: #67e8f9;
    --accent-bg: rgba(45, 212, 191, 0.1);

    /* THUỘC TÍNH BO GÓC THỐNG NHẤT */
    --radius-md: 12px;
    --radius-lg: 20px;
}

body, html { 
    background-color: var(--bg-main) !important; 
    font-family: 'Inter', sans-serif !important; 
    color: var(--text-main) !important; 
    margin: 0 !important; 
    padding: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important; 
}
.gradio-container { 
    max-width: 100% !important; 
    width: 100% !important; 
    padding: 0 !important; 
    margin: 0 !important; 
    border: none !important; 
    background: transparent !important; 
}
footer { display: none !important; }

/* ---------------- BỐ CỤC CHÍNH ---------------- */
#main-container {
    display: flex;
    flex-direction: row;
    width: 100%;
    max-width: 1500px;
    margin: 0 auto;
    height: 100vh;
    padding: 20px;
    box-sizing: border-box;
    gap: 30px;
    align-items: stretch;
}

/* ---------------- CỘT KẾT QUẢ LAPTOP (TRÁI) ---------------- */
#results-col {
    width: 50% !important;
    height: 100%;
    overflow-y: auto;
    padding-right: 15px;
}

/* ---------------- CỘT CHATBOT (PHẢI HOẶC GIỮA) ---------------- */
.chat-col {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    transition: all 0.4s ease-in-out;
}
.chat-col.center { 
    max-width: 800px !important; 
    margin: 0 auto; 
    justify-content: center; 
}
.chat-col.side { 
    width: 50% !important; 
    max-width: 800px !important; 
    margin: 0; 
    justify-content: flex-end; 
}

/* ---------------- GREETING TRÊN INPUT ---------------- */
#greeting-block {
    text-align: center;
    margin-bottom: 24px;
}
#greeting-block h1 {
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-main);
}

/* ---------------- BONG BÓNG CHAT LLM ---------------- */
.gradio-chatbot { 
    background: transparent !important; 
    border: none !important; 
    flex-grow: 1 !important; 
    height: 0 !important; 
    overflow-y: auto !important; 
}
.message.bot { 
    background: transparent !important; 
    border: none !important; 
    color: var(--text-main) !important; 
    font-size: 1.05rem !important; 
    padding-left: 0 !important; 
}
.message.user { 
    background: var(--bg-input) !important; 
    border: none !important; 
    color: var(--text-main) !important; 
    font-size: 1.05rem !important; 
    border-radius: 20px !important; 
    padding: 12px 18px !important; 
    margin-left: auto !important; 
    max-width: 80% !important; 
}

/* ---------------- THANH INPUT KIỂU “ASK ANYTHING” (1 LỚP) ---------------- */
.input-row { 
    background: #252525 !important;          /* màu nền thanh */
    padding: 10px 18px !important;
    border-radius: 999px !important;         /* pill tròn */
    align-items: center !important;
    width: 100% !important;
    flex-shrink: 0 !important;
    box-shadow: none !important;
    margin-bottom: 10px !important;
    border: 1px solid #3a3a3a;
}
.input-row:focus-within {
    border-color: #4b4b4b !important;
}

/* textarea trùng màu với bounding -> nhìn như 1 lớp */
.input-row textarea { 
    background: #252525 !important;          /* cùng màu .input-row */
    border: none !important;
    box-shadow: none !important;
    color: var(--text-main) !important; 
    font-size: 1.05rem !important; 
}
.input-row input,
.input-row .wrap,
.input-row .container,
.input-row .input-container,
.input-row .gr-text-input {
    background: #252525 !important;
    border: none !important;
    box-shadow: none !important;
}
.input-row textarea::focus { outline: none !important; }
.input-row textarea::placeholder { color: #b3b3b3 !important; }

/* Nút gửi tròn nhỏ bên phải */
.send-btn { 
    background: #3a3a3a !important; 
    color: #f5f5f5 !important; 
    border-radius: 999px !important; 
    width: 36px !important; 
    height: 36px !important; 
    min-width: 36px !important; 
    padding: 0 !important; 
    display: flex; 
    justify-content: center; 
    align-items: center; 
    border: none !important; 
    font-size: 1.1rem !important; 
    cursor: pointer; 
    transition: background 0.15s, transform 0.15s;
}
.send-btn:hover { 
    background: #4a4a4a !important; 
    transform: scale(1.03); 
}

/* NÚT LÀM MỚI (DƯỚI CÙNG) */
.clear-btn { 
    background: transparent !important; 
    border: none !important; 
    color: #888 !important; 
    font-size: 0.85rem !important; 
    text-align: center; 
    cursor: pointer; 
    box-shadow: none !important; 
    flex-shrink: 0; 
    padding: 5px !important;
}
.clear-btn:hover { color: var(--text-main) !important; }

/* --------- PHẦN CARD LAPTOP (GIỮ NGUYÊN TỪ CODE CŨ) --------- */
.result-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 20px; padding-bottom: 40px; }
.card-wrapper { position: relative; width: 100%; transition: all 0.3s ease; }
.laptop-card { background: var(--bg-surface) !important; border: 1px solid var(--border-color) !important; border-radius: var(--radius-md) !important; padding: 15px !important; transition: all 0.3s ease !important; display: flex; flex-direction: column; gap: 10px; height: 100%;}
.laptop-card:hover:not(.expanded) { transform: translateY(-5px); border-color: var(--accent) !important; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important; }
.laptop-name { font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin-bottom: 4px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.laptop-price { font-size: 1.3rem; font-weight: 800; color: var(--accent); }
.badges { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 5px; }
.badge { font-size: 0.75rem; padding: 4px 8px; border-radius: 6px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; background: var(--bg-main); color: var(--text-main); border: 1px solid var(--border-color);}
.badge-similarity { background: var(--accent-bg); color: var(--accent); border: 1px solid var(--accent); }
.specs-row { display: flex; justify-content: space-between; padding-top: 10px; border-top: 1px solid var(--border-color); color: var(--text-sub); font-size: 0.9rem; }
.view-detail-btn { margin-top: auto; width: 100%; background: var(--bg-main); border: none; color: var(--text-main); padding: 10px; border-radius: 8px; cursor: pointer; transition: 0.2s; font-weight: 600; font-size: 0.95rem; border: 1px solid var(--border-color);}
.view-detail-btn:hover { background: var(--accent); color: var(--text-inverse); }
.detail-section { margin-top: 15px; padding-top: 15px; border-top: 1px dashed var(--border-color); }
.detail-section:first-child { border-top: none; padding-top: 0; }
.specs-list { list-style: none; padding: 0; margin: 0; color: var(--text-sub); font-size: 0.95rem; }
.specs-list li { margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid var(--border-color); display: flex; align-items: flex-start; line-height: 1.4; }
.specs-list li b { color: var(--text-main); width: 100px; flex-shrink: 0; font-weight: 600; }
.review-item { margin-bottom: 10px; padding: 12px; background: var(--bg-main); border-radius: 8px; border-left: 3px solid var(--accent); color: var(--text-main); font-size: 0.95rem; line-height: 1.6; }
.review-item i { margin-right: 6px; color: var(--text-sub); font-size: 1.1rem; }

.result-grid.has-expanded .card-wrapper:not(.is-active) { opacity: 0.2 !important; filter: blur(3px) !important; pointer-events: none !important; transform: scale(0.98); }
.laptop-card.expanded { z-index: 9999 !important; background: var(--bg-surface) !important; border: 1px solid var(--accent) !important; box-shadow: 0 40px 100px rgba(0,0,0,0.8) !important; max-height: 85vh !important; overflow-y: auto !important; animation: popModal 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards !important; border-radius: var(--radius-lg) !important; }
.laptop-card.expanded::-webkit-scrollbar { width: 8px; }
.laptop-card.expanded::-webkit-scrollbar-track { background: transparent; }
.laptop-card.expanded::-webkit-scrollbar-thumb { background: #565869; border-radius: 10px; }
.laptop-card.expanded .laptop-name { font-size: 1.4rem; -webkit-line-clamp: unset; }
.laptop-card.expanded .laptop-price { font-size: 1.6rem; }
.card-detail { margin-top: 15px; padding-top: 15px; border-top: 1px dashed var(--border-color); animation: fadeIn 0.4s ease-in-out; }
.detail-title { color: var(--text-main); font-weight: 700; margin-bottom: 12px; font-size: 1.1rem; text-transform: uppercase; }

.laptop-card.expanded .view-detail-btn { 
    background: transparent !important; 
    color: var(--accent) !important; 
    border: 1px solid var(--accent) !important; 
    margin-top: 20px;
    position: sticky !important;
    bottom: -1px !important;
    z-index: 100 !important;
    box-shadow: 0 -10px 20px var(--bg-surface) !important;
}
.laptop-card.expanded .view-detail-btn:hover { background: var(--accent) !important; color: var(--text-inverse) !important; }

@keyframes popModal { 0% { opacity: 0; transform: translate(-50%, -45%) scale(0.9); } 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #565869; border-radius: 10px; }

/* ---------------- TẮT KHUNG LOADING MẶC ĐỊNH CỦA GRADIO ---------------- */
div[class*="generating"], .wrap.generating, .generating {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

.progress-text {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}

/* Ẩn thanh chạy ngang (nếu có) để nhìn sạch sẽ hơn, chỉ giữ lại số giây */
.eta-bar {
    display: none !important;
}
"""

# =========================
# JAVASCRIPT
# =========================
head_js = """
<script>
    document.documentElement.classList.add('dark');
</script>
"""

auto_scroll_js = """
function() {
    setTimeout(function() {
        let chatContainers = document.querySelectorAll('.gradio-chatbot .overflow-y-auto, .gradio-chatbot [class*="overflow-"]');
        chatContainers.forEach(container => { 
            container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' }); 
        });
    }, 100);
}
"""

toggle_layout_js = """
function(html) {
    if(html && html.includes('result-grid')) {
        document.body.classList.add('show-results'); 
    }
}
"""

clear_layout_js = """
function() {
    document.body.classList.remove('show-results');
}
"""

# =========================
# KHỞI TẠO GIAO DIỆN CHÍNH
# =========================
with gr.Blocks(css=custom_css, head=head_js, theme=gr.themes.Base()) as interface:
    session_memory = gr.State(value="")
    chat_history   = gr.State(value=[]) 

    with gr.Row(elem_id="main-container"):
        
        with gr.Column(elem_id="results-col", visible=False) as results_col:
            output_display = gr.HTML(label="Kết quả", show_label=False)

        with gr.Column(elem_classes=["chat-col", "center"], elem_id="chat-col") as chat_col:
            
            hero_title = gr.HTML("""
            <div id="greeting-block">
                <h1>How can I help?</h1>
            </div>
            """, visible=True)
            
            chatbot_ui = gr.Chatbot(
                value=[], 
                show_label=False,
                elem_classes=["gradio-chatbot"],
                autoscroll=True,
                visible=False 
            )
            
            with gr.Row(elem_classes=["input-row"]):
                query_input = gr.Textbox(
                    show_label=False, 
                    placeholder="Ask about laptops",
                    lines=1,
                    scale=8,
                    container=False
                )
                submit_btn = gr.Button("➤", elem_classes=["send-btn"], scale=1)
            
            clear_btn = gr.Button(
                "Bắt đầu cuộc hội thoại mới",
                elem_classes=["clear-btn"],
                visible=False
            )

    # ==== SỰ KIỆN ====
    sub_evt = submit_btn.click(
        fn=chat_logic, 
        inputs=[query_input, session_memory, chat_history, chatbot_ui], 
        outputs=[output_display, session_memory, chat_history, chatbot_ui,
                 query_input, results_col, chat_col, hero_title, chatbot_ui, clear_btn]
    )
    sub_evt.then(fn=None, inputs=None, outputs=None, js=auto_scroll_js)
    sub_evt.then(fn=None, inputs=[output_display], outputs=None, js=toggle_layout_js)
    
    ent_evt = query_input.submit(
        fn=chat_logic, 
        inputs=[query_input, session_memory, chat_history, chatbot_ui], 
        outputs=[output_display, session_memory, chat_history, chatbot_ui,
                 query_input, results_col, chat_col, hero_title, chatbot_ui, clear_btn]
    )
    ent_evt.then(fn=None, inputs=None, outputs=None, js=auto_scroll_js)
    ent_evt.then(fn=None, inputs=[output_display], outputs=None, js=toggle_layout_js)
    
    clear_btn.click(
        fn=reset_all, 
        inputs=None, 
        outputs=[output_display, session_memory, chat_history, chatbot_ui,
                 query_input, results_col, chat_col, hero_title, chatbot_ui, clear_btn]
    ).then(fn=None, inputs=None, outputs=None, js=clear_layout_js)

if __name__ == "__main__":
    interface.launch(inbrowser=True)
