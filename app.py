import streamlit as st
from datetime import datetime, timedelta
import io
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn  # 用來設定中文字型的重要元件

# =========================================================
# 0) 基礎設定
# =========================================================
PROVIDER_NAME = "高如慧"
BANK_NAME = "中國信託商業銀行"
BANK_CODE = "822"
ACCOUNT_NUMBER = "783540208870"

# =========================================================
# 1) Page config
# =========================================================
st.set_page_config(
    page_title="廣告投放合約生成器 (Word版)",
    page_icon="📝",
    layout="centered"
)

st.title("📝 廣告投放合約生成器")
st.caption("✅ 解決字型問題：直接生成 Word 檔，下載後請自行轉存 PDF。")
st.markdown("---")

# =========================================================
# 2) Session state
# =========================================================
if "generated" not in st.session_state:
    st.session_state.generated = False
    st.session_state.client_message = ""
    st.session_state.payment_message = ""
    st.session_state.docx_bytes = b""
    st.session_state.last_party_a_name = ""

# =========================================================
# 3) Word 字型設定函式 (關鍵：強制使用微軟正黑體)
# =========================================================
def set_run_font(run, size=12, bold=False):
    """設定字型為微軟正黑體，避免 Word 預設的新細明體或無襯線體"""
    run.font.name = 'Microsoft JhengHei'
    run.font.size = Pt(size)
    run.bold = bold
    # 下面這行是讓 Word 識別中文字型的關鍵
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft JhengHei')

# =========================================================
# 4) 生成 Word 邏輯
# =========================================================
def generate_docx_bytes(party_a, payment_opt, start_dt, pay_day, pay_dt):
    doc = Document()
    
    # --- 設定整份文件的預設行距 ---
    style = doc.styles['Normal']
    style.paragraph_format.line_spacing = 1.5 # 1.5倍行高，比較好閱讀

    # --- 標題 ---
    heading = doc.add_paragraph()
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = heading.add_run("廣告投放服務合約書")
    set_run_font(run, size=18, bold=True)
    doc.add_paragraph("") # 空行

    # --- 計算變數 ---
    if payment_opt == "17,000元/月（每月付款）":
        end_dt = start_dt + timedelta(days=30)
        period_text = (f"自 {start_dt.strftime('%Y 年 %m 月 %d 日')} 起至 {end_dt.strftime('%Y 年 %m 月 %d 日')} 止，共 1 個月。"
                       "届期如雙方無異議，則本合約自動續行 1 個月，以此類推。")
        price_text = "1. 甲方同意支付乙方服務費用 新台幣壹萬柒仟元整（NT$17,000）／月。"
        pay_time_text = f"2. 付款時間：甲方應於每月 {pay_day} 日前支付當月服務費用至乙方指定帳戶。"
        first_pay_text = f"3. 首期款項應於合作啟動日（{start_dt.strftime('%Y 年 %m 月 %d 日')}）前支付完成。"
        refund_text = "2. 月付方案：已支付之當期費用不予退還。"
    else:
        end_dt = start_dt + timedelta(days=90)
        period_text = (f"自 {start_dt.strftime('%Y 年 %m 月 %d 日')} 起至 {end_dt.strftime('%Y 年 %m 月 %d 日')} 止，共 3 個月。"
                       "届期如雙方有意續約，應於届滿前 7 日另行協議。")
        price_text = "1. 甲方同意支付乙方服務費用 新台幣肆萬伍仟元整（NT$45,000）／三個月。"
        pay_time_text = f"2. 付款時間：甲方應於 {pay_dt.strftime('%Y 年 %m 月 %d 日')} 前一次支付完成。"
        first_pay_text = None
        refund_text = "2. 季付方案屬優惠性質之預付服務費，一經支付後即不予退還。即使甲方於合約期間內提前終止或未使用完畢服務內容，亦同；惟因乙方重大違約致服務無法履行者，不在此限。"

    # --- 立約人 ---
    p = doc.add_paragraph()
    run = p.add_run(f"甲方（委託暨付款方）：{party_a}\n")
    set_run_font(run, size=12, bold=True)
    run = p.add_run(f"乙方（服務執行者）：{PROVIDER_NAME}")
    set_run_font(run, size=12, bold=True)
    doc.add_paragraph("")

    # --- 前言 ---
    p = doc.add_paragraph()
    run = p.add_run("茲因甲方委託乙方提供數位廣告投放服務，雙方本於誠信原則，同意訂立本合約，並共同遵守下列條款：")
    set_run_font(run)

    # --- 通用條款加入函式 ---
    def add_clause(title, contents):
        p_title = doc.add_paragraph()
        run_title = p_title.add_run(title)
        set_run_font(run_title, size=12, bold=True)
        
        for content in contents:
            if content:
                p_item = doc.add_paragraph()
                p_item.paragraph_format.left_indent = Cm(0.75) # 縮排
                # 處理 content 可能包含粗體需求（這裡簡化處理，全部正常字體）
                run_item = p_item.add_run(content)
                set_run_font(run_item)

    # --- 第一條 ---
    add_clause("第一條　合約期間", [period_text])

    # --- 第二條 ---
    doc.add_paragraph("")
    p = doc.add_paragraph()
    run = p.add_run("第二條　服務內容")
    set_run_font(run, bold=True)
    
    p = doc.add_paragraph()
    run = p.add_run("乙方同意為甲方提供以下廣告投放服務：")
    p.paragraph_format.left_indent = Cm(0)
    set_run_font(run)

    # 二-1
    p = doc.add_paragraph()
    run = p.add_run("一、固定工作項目")
    p.paragraph_format.left_indent = Cm(0.75)
    set_run_font(run, bold=True)

    items_fixed = [
        "1. 廣告上架：依甲方需求於指定平台建立並上架廣告活動。",
        "2. 廣告監控／維護／優化：定期監控成效數據，進行必要之調整與優化。",
        "3. 簡易週報：每週提供廣告成效摘要及下週優化方向。"
    ]
    for item in items_fixed:
        p = doc.add_paragraph(item)
        p.paragraph_format.left_indent = Cm(1.5)
        set_run_font(p.runs[0])

    # 二-2
    p = doc.add_paragraph()
    run = p.add_run("二、非固定工作項目（視實際狀況提供）")
    p.paragraph_format.left_indent = Cm(0.75)
    set_run_font(run, bold=True)

    items_non = [
        "1. 廣告素材建議：乙方得依投放成效、競品與市場狀況，提供素材與文案方向建議。",
        "2. 到達頁面優化建議：於轉換成效異常或下降時，提供頁面優化方向。"
    ]
    for item in items_non:
        p = doc.add_paragraph(item)
        p.paragraph_format.left_indent = Cm(1.5)
        set_run_font(p.runs[0])

    # --- 第三條 ---
    add_clause("第三條　服務範圍與限制", [
        "1. 本服務範圍以 Meta（Facebook／Instagram）廣告投放為主；若需擴展至其他平台，雙方另行協議。",
        "2. 廣告投放預算由甲方自行支付予廣告平台，不包含於本合約服務費用內。",
        "3. 廣告素材（圖片、影片等）之製作原則上由甲方提供，乙方提供方向與建議。",
        "4. 甲方應提供必要帳號權限、素材與資訊，以確保服務得以順利執行。"
    ])

    # --- 第四條 ---
    add_clause("第四條　配合事項與作業方式", [
        "1. 甲方同意配合乙方所需之資料提供、權限設定與必要操作，以確保服務品質。",
        "2. 若因平台政策、帳號狀況或其他不可控因素需採替代作業方式（例如：由甲方匯出報表供乙方監控），甲方同意合理配合。"
    ])

    # --- 第五條 ---
    add_clause("第五條　費用與付款方式", [
        price_text,
        pay_time_text,
        first_pay_text,
        "4. 逾期付款者，乙方得暫停服務至款項付清為止；因此造成之廣告中斷或成效波動，乙方不負賠償責任。"
    ])

    # 收款帳號 (縮排顯示)
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.5)
    run = p.add_run(f"乙方指定收款帳戶：\n銀行：{BANK_NAME}（{BANK_CODE}）\n帳號：{ACCOUNT_NUMBER}")
    set_run_font(run)

    # --- 第六條 ---
    add_clause("第六條　付款方式與稅務責任", [
        "1. 乙方為自然人，依法無須開立統一發票。",
        "2. 本合約費用之付款方式、帳務處理及相關稅務申報，均由甲方依其自身狀況及相關法令自行決定並負責。",
        "3. 甲方得依其帳務或實務需求，選擇是否以勞務報酬方式支付或其他合法方式付款；乙方將於合理需求下配合提供必要之收款或服務文件。",
        "4. 乙方不負責判斷、建議或保證任何稅務處理方式之合法性。"
    ])

    # --- 第七條 ---
    add_clause("第七條　成效聲明與免責", [
        "1. 乙方將盡專業所能優化廣告成效，但投放成效受市場環境、競爭狀況、消費者行為、平台演算法等多重因素影響，乙方不保證特定之轉換率、ROAS 或銷售成果。",
        "2. 因平台政策變更、帳號異常、不可抗力因素等非乙方可控原因導致之廣告中斷或成效下降，乙方不負賠償責任。",
        "3. 甲方提供之素材、商品或服務如違反平台政策或法令規定，導致廣告被拒絕或帳號受處分，乙方不負相關責任。"
    ])

    # --- 第八條 ---
    add_clause("第八條　保密條款", [
        "1. 合作期間所涉及之商業資訊、廣告數據、行銷策略及客戶資料等，均屬機密資訊，僅得用於本合作目的。",
        "2. 本保密義務於合約終止後仍持續有效 2 年。"
    ])

    # --- 第九條 ---
    add_clause("第九條　智慧財產權", [
        "1. 乙方提供之廣告文案、策略建議、報告等成果，甲方於付清全部款項後，得於本案範圍內使用。",
        "2. 甲方提供之品牌素材、商標、圖片等，其權利仍歸甲方所有。"
    ])

    # --- 第十條 ---
    add_clause("第十條　合約終止", [
        "1. 任一方如欲提前終止本合約，應於終止日前 14 日以書面（含電子郵件、通訊軟體訊息）通知他方。",
        refund_text,
        "3. 如因一方重大違約致他方權益受損，受損方得立即終止合約並請求損害賠償。"
    ])

    # --- 第十一條 ---
    add_clause("第十一條　通知方式", [
        "本合約相關通知，得以電子郵件、LINE、Messenger 或其他雙方約定之通訊方式為之，於發送時即生效力。"
    ])

    # --- 第十二條 ---
    add_clause("第十二條　合約變更", [
        "本合約之任何修改或補充，應經雙方書面同意後始生效力。"
    ])

    # --- 第十三條 ---
    add_clause("第十三條　不可抗力", [
        "因天災、戰爭、政府行為、網路中斷、平台系統異常或其他不可抗力因素，致任一方無法履行本合約義務時，該方不負違約責任；惟應儘速通知並於事由消滅後恢復履行。"
    ])

    # --- 第十四條 ---
    add_clause("第十四條　爭議處理", [
        "本合約之解釋與適用，以中華民國法律為準據法。雙方如有爭議，應先行協商；協商不成以臺灣臺北地方法院為第一審管轄法院。"
    ])

    # --- 簽名欄 (使用表格排版) ---
    doc.add_paragraph("")
    doc.add_paragraph("")
    
    table = doc.add_table(rows=3, cols=2)
    table.autofit = False
    
    # 甲方欄位
    cell_a = table.cell(0, 0)
    run = cell_a.paragraphs[0].add_run(f"甲方（委託暨付款方）：\n{party_a}\n\n簽名：___________________\n\n日期：_____ 年 ___ 月 ___ 日")
    set_run_font(run, size=12)

    # 乙方欄位
    cell_b = table.cell(0, 1)
    run = cell_b.paragraphs[0].add_run(f"乙方（服務執行者）：\n{PROVIDER_NAME}\n\n簽名：___________________\n\n日期：_____ 年 ___ 月 ___ 日")
    set_run_font(run, size=12)

    # 寫入 Buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# =========================================================
# 5) UI: 輸入與互動
# =========================================================
st.header("服務內容說明")
st.subheader("✅ 固定工作")
st.markdown("""
- **廣告上架**
- **廣告監控 / 維護 / 優化**
- **簡易週報**（成果摘要、下週優化方向）
""")

st.subheader("📌 非固定工作（視狀況提供）")
st.markdown("""
- **廣告素材建議**
  - 依投放成效、競品、市場狀況提出方向
- **到達頁面優化建議**
  - 監控轉換成效
""")

st.warning("📌 稅務提醒：乙方為自然人，無須開立發票。甲方自行處理勞報或相關稅務。")
st.markdown("---")

# --- 方案 ---
st.header("💰 付款方案")
payment_option = st.radio(
    "方案選擇：",
    options=["17,000元/月（每月付款）", "45,000元/三個月（一次付款）"]
)

# --- 日期 ---
st.header("📅 時間設定")
default_start = datetime.now().date() + timedelta(days=7)
start_date = st.date_input("合作啟動日", value=default_start)

payment_day = None
payment_date = None

if payment_option == "17,000元/月（每月付款）":
    payment_day = st.slider("每月付款日", 1, 28, 5)
else:
    default_pay = start_date - timedelta(days=3)
    if default_pay < datetime.now().date(): default_pay = datetime.now().date()
    payment_date = st.date_input("付款日期", value=default_pay)

st.markdown("---")

# --- 資料輸入 ---
st.header("🧾 甲方資訊")
party_a_name = st.text_input("甲方名稱", placeholder="公司或個人名稱")

st.header("👤 乙方資訊")
st.text_input("乙方", value=PROVIDER_NAME, disabled=True)
c1, c2 = st.columns(2)
c1.text_input("銀行", value=f"{BANK_NAME} ({BANK_CODE})", disabled=True)
c2.text_input("帳號", value=ACCOUNT_NUMBER, disabled=True)

st.markdown("---")

# =========================================================
# 6) 生成按鈕
# =========================================================
st.header("✅ 生成合約")

if st.button("📝 生成 Word 合約", type="primary", use_container_width=True):
    if not party_a_name.strip():
        st.error("請輸入甲方名稱")
    else:
        # 準備確認訊息
        if payment_option == "17,000元/月（每月付款）":
            client_msg = f"""【合約確認】
甲方：{party_a_name}
乙方：{PROVIDER_NAME}
方案：17,000元/月
啟動：{start_date}
付款：每月 {payment_day} 日"""
        else:
            client_msg = f"""【合約確認】
甲方：{party_a_name}
乙方：{PROVIDER_NAME}
方案：45,000元/季
啟動：{start_date}
付款：{payment_date} 前"""

        payment_msg = f"""【收款資訊】
銀行：{BANK_NAME} ({BANK_CODE})
帳號：{ACCOUNT_NUMBER}"""

        # 生成 DOCX
        docx_bytes = generate_docx_bytes(
            party_a_name, payment_option, start_date, payment_day, payment_date
        )

        st.session_state.client_message = client_msg
        st.session_state.payment_message = payment_msg
        st.session_state.docx_bytes = docx_bytes
        st.session_state.generated = True
        st.session_state.last_party_a_name = party_a_name
        
        st.success("✅ Word 合約已生成！")

# =========================================================
# 7) 下載區
# =========================================================
if st.session_state.generated:
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.text_area("給甲方的訊息", value=st.session_state.client_message, height=150)
    with c2:
        st.text_area("收款資訊", value=st.session_state.payment_message, height=150)
    
    filename = f"廣告投放合約_{st.session_state.last_party_a_name}_{datetime.now().strftime('%Y%m%d')}.docx"
    
    st.download_button(
        label="⬇️ 下載 Word 合約 (.docx)",
        data=st.session_state.docx_bytes,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True
    )
    
    st.info("💡 下載後，建議直接在 Word 中『另存新檔 -> PDF』，即可獲得完美排版。")
    
    if st.button("重置"):
        st.session_state.generated = False
        st.rerun()
