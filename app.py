import streamlit as st
from docx import Document
from io import BytesIO

# --- 頁面設定 ---
st.set_page_config(page_title="專案交付與請款生成器", page_icon="📄")

st.title("📄 專案交付與請款助手")
st.write("填寫下方資訊，自動生成給客戶的信件範本、收款資訊以及 Word 文件。")

# --- 側邊欄：輸入資料 ---
with st.sidebar:
    st.header("📝 專案資訊輸入")
    client_name = st.text_input("客戶名稱", value="泛泰科技")
    project_name = st.text_input("專案名稱", value="2025 Q1 數位轉型顧問案")
    amount = st.number_input("請款金額", value=50000, step=1000)
    due_date = st.date_input("預計付款日")

# --- 核心邏輯區 ---

# 1. 定義這兩段要讓使用者複製的文字
# 可以在這裡修改你的預設信件模板
message_content = f"""{client_name} 您好：

感謝您的委託，關於「{project_name}」專案，目前已執行完畢。
附件為本次的結案報告與請款單，請您查收。

若內容確認無誤，再麻煩協助安排款項。
期待未來能有再次合作的機會！

祝 順心
高如慧 (Dennis)"""

# 可以在這裡修改你的銀行帳戶
payment_info = f"""【匯款資訊】
銀行代碼：822 (中國信託)
分行名稱：市府分行
帳戶號碼：123-456-789012
戶名：高如慧
應付金額：NT$ {amount:,}"""

# 2. 生成 Word 文件的函數 (解決你原本的 docx 錯誤)
def generate_docx():
    doc = Document()
    doc.add_heading('專案請款單', 0)
    
    doc.add_paragraph(f'客戶名稱：{client_name}')
    doc.add_paragraph(f'專案名稱：{project_name}')
    doc.add_paragraph(f'應付金額：NT$ {amount:,}')
    doc.add_paragraph(f'付款期限：{due_date}')
    
    doc.add_heading('匯款資訊', level=1)
    doc.add_paragraph('銀行：中國信託 (822)\n帳號：123-456-789012\n戶名：高如慧')
    
    # 將檔案存入記憶體 (BytesIO)，而不是硬碟，適合 Streamlit Cloud
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 顯示輸出結果 ---

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 給甲方的訊息")
    st.caption("點擊右上角按鈕即可複製傳送")
    # 關鍵：使用 st.code 搭配 language=None 實現複製功能
    st.code(message_content, language=None)

with col2:
    st.subheader("2. 收款資訊")
    st.caption("點擊右上角按鈕即可複製")
    # 關鍵：使用 st.code 搭配 language=None 實現複製功能
    st.code(payment_info, language=None)

st.divider()

# --- 下載 Word 檔區塊 ---
st.subheader("3. 下載正式文件")
docx_file = generate_docx()

st.download_button(
    label="📥 下載 Word 請款單 (.docx)",
    data=docx_file,
    file_name=f"請款單_{client_name}_{project_name}.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
