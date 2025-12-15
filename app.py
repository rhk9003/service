import streamlit as st
from datetime import datetime, timedelta
import io
import os
from pathlib import Path
import requests

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# =========================================================
# 0) 預設值（你可以留著，不用每次改程式）
# =========================================================
DEFAULT_PARTY_B_NAME = "高如慧"  # 乙方（服務執行者）
DEFAULT_BANK_NAME = "中國信託商業銀行"
DEFAULT_BANK_CODE = "822"
DEFAULT_ACCOUNT_NUMBER = "783540208870"

# 字型（自動下載到 ./.cache/fonts）
FONT_NAME = "NotoSansTC"
FONT_FILE_NAME = "NotoSansTC-Regular.ttf"
FONT_URLS = [
    # 優先：raw.githubusercontent.com（通常最穩）
    "https://raw.githubusercontent.com/googlefonts/noto-sans-tc/main/fonts/ttf/NotoSansTC-Regular.ttf",
    # 備援：github raw
    "https://github.com/googlefonts/noto-sans-tc/raw/main/fonts/ttf/NotoSansTC-Regular.ttf",
]

APP_DIR = Path(__file__).resolve().parent
FONT_DIR = APP_DIR / ".cache" / "fonts"
FONT_PATH = FONT_DIR / FONT_FILE_NAME


# =========================================================
# 1) Page config
# =========================================================
st.set_page_config(
    page_title="廣告投放服務合約產生器",
    page_icon="📋",
    layout="centered"
)

st.title("📋 廣告投放服務合約產生器（角色翻正版）")
st.caption("甲方＝委託暨付款方（客戶）；乙方＝服務執行者（你）")
st.markdown("---")


# =========================================================
# 2) Session state：避免下載後清空
# =========================================================
if "generated" not in st.session_state:
    st.session_state.generated = False
    st.session_state.client_message = ""
    st.session_state.payment_message = ""
    st.session_state.pdf_bytes = b""
    st.session_state.last_party_a_name = ""


# =========================================================
# 3) 字型：自動下載 + 註冊（只下載一次）
# =========================================================
def ensure_font_loaded():
    FONT_DIR.mkdir(parents=True, exist_ok=True)

    if not FONT_PATH.exists():
        last_err = None
        with st.spinner("正在下載中文字型（僅第一次需要）..."):
            for url in FONT_URLS:
                try:
                    resp = requests.get(url, timeout=30)
                    resp.raise_for_status()
                    FONT_PATH.write_bytes(resp.content)
                    break
                except Exception as e:
                    last_err = e
            else:
                st.error("字型下載失敗，請確認網路可連線，或稍後再試。")
                if last_err:
                    st.exception(last_err)
                st.stop()

    # 註冊字型（避免重複）
    try:
        pdfmetrics.getFont(FONT_NAME)
    except KeyError:
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))


# =========================================================
# 4) UI：服務內容
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
  - 依投放成效、競品、市場研究提出方向
  - 提供文案與素材文字建議供調整
- **到達頁面優化建議**
  - 監控轉換成效
  - 轉換異常或下降時提供優化方向
""")

st.warning("""
📌 稅務/帳務提醒  
- 乙方為自然人，無須開立統一發票。  
- 甲方是否採用勞務報酬（扣繳/勞報）或其他合法付款方式，皆由甲方依其內規與法令自行決定並負責；乙方不提供稅務判斷。
""")

st.markdown("---")


# =========================================================
# 5) UI：方案
# =========================================================
st.header("💰 付款方案選擇")
payment_option = st.radio(
    "請選擇方案：",
    options=[
        "17,000元/月（每月付款）",
        "45,000元/三個月（一次付款）"
    ],
    index=0
)

st.markdown("---")


# =========================================================
# 6) UI：合作時間
# =========================================================
st.header("📅 合作時間設定")

default_start = datetime.now().date() + timedelta(days=7)
start_date = st.date_input(
    "合作啟動日期",
    value=default_start,
    min_value=datetime.now().date()
)

payment_day = None
payment_date = None

if payment_option == "17,000元/月（每月付款）":
    payment_day = st.slider(
        "每月付款日（例如：每月5號）",
        min_value=1,
        max_value=28,
        value=5
    )
    total_amount_text = "17,000元/月"
    contract_type = "月付方案"
else:
    default_payment = start_date - timedelta(days=3)
    if default_payment < datetime.now().date():
        default_payment = datetime.now().date()

    payment_date = st.date_input(
        "付款日期（建議於合作啟動前完成付款）",
        value=default_payment,
        min_value=datetime.now().date(),
        max_value=start_date
    )
    total_amount_text = "45,000元（三個月）"
    contract_type = "季付方案"

st.markdown("---")


# =========================================================
# 7) UI：甲乙方資訊（角色翻正）
# =========================================================
st.header("🧾 甲方資訊（委託暨付款方）")
party_a_name = st.text_input("甲方名稱/公司名稱", placeholder="請輸入付款方名稱（公司或個人）")

st.markdown("---")

st.header("👤 乙方資訊（服務執行者）")
party_b_name = st.text_input("乙方名稱", value=DEFAULT_PARTY_B_NAME)

st.subheader("💳 乙方收款資訊")
bank_name = st.text_input("銀行名稱", value=DEFAULT_BANK_NAME)
bank_code = st.text_input("銀行代碼", value=DEFAULT_BANK_CODE)
account_number = st.text_input("帳號", value=DEFAULT_ACCOUNT_NUMBER)

st.markdown("---")


# =========================================================
# 8) 產生 PDF（bytes）
# =========================================================
def generate_pdf_bytes(
    party_a_name: str,
    party_b_name: str,
    bank_name: str,
    bank_code: str,
    account_number: str,
    payment_option: str,
    start_date,
    payment_day: int | None,
    payment_date,
):
    ensure_font_loaded()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    styles = {
        'title': ParagraphStyle('Title', fontName=FONT_NAME, fontSize=18, alignment=1, spaceAfter=14),
        'heading': ParagraphStyle('Heading', fontName=FONT_NAME, fontSize=12, spaceBefore=10, spaceAfter=6),
        'party': ParagraphStyle('Party', fontName=FONT_NAME, fontSize=11, leading=16, spaceAfter=2),
        'normal': ParagraphStyle('Normal', fontName=FONT_NAME, fontSize=10, leading=16, firstLineIndent=20),
        'normal_no_indent': ParagraphStyle('NormalNoIndent', fontName=FONT_NAME, fontSize=10, leading=16),
        'number_item': ParagraphStyle('NumberItem', fontName=FONT_NAME, fontSize=10, leftIndent=15, leading=15, spaceAfter=2),
        'bank_info': ParagraphStyle('BankInfo', fontName=FONT_NAME, fontSize=10, leftIndent=15, leading=15, spaceAfter=1),
    }

    story = []
    story.append(Paragraph("<b>廣告投放服務合約書</b>", styles['title']))

    # 合約期間文字
    if payment_option == "17,000元/月（每月付款）":
        contract_end = start_date + timedelta(days=30)
        contract_period_text = (
            f"自 {start_date.strftime('%Y 年 %m 月 %d 日')} 起至 {contract_end.strftime('%Y 年 %m 月 %d 日')} 止，共 1 個月。"
            "届期如雙方無異議，則本合約自動續行 1 個月，以此類推。"
        )
    else:
        contract_end = start_date + timedelta(days=90)
        contract_period_text = (
            f"自 {start_date.strftime('%Y 年 %m 月 %d 日')} 起至 {contract_end.strftime('%Y 年 %m 月 %d 日')} 止，共 3 個月。"
            "届期如雙方有意續約，應於届滿前 7 日另行協議。"
        )

    # 甲乙方（翻正）
    story.append(Paragraph(f"<b>甲方（委託暨付款方）：</b>{party_a_name}", styles['party']))
    story.append(Paragraph(f"<b>乙方（服務執行者）：</b>{party_b_name}", styles['party']))
    story.append(Spacer(1, 8))

    # 前言
    story.append(Paragraph(
        "茲因甲方委託乙方提供數位廣告投放服務，雙方本於誠信原則，同意訂立本合約，並共同遵守下列條款：",
        styles['normal']
    ))

    # 第一條：合約期間
    story.append(Paragraph("<b>第一條　合約期間</b>", styles['heading']))
    story.append(Paragraph(contract_period_text, styles['normal']))

    # 第二條：服務內容
    story.append(Paragraph("<b>第二條　服務內容</b>", styles['heading']))
    story.append(Paragraph("乙方同意為甲方提供以下廣告投放服務：", styles['normal_no_indent']))

    story.append(Paragraph("<b>一、固定工作項目</b>", styles['normal_no_indent']))
    story.append(Paragraph("1. 廣告上架：依甲方需求於指定平台建立並上架廣告活動。", styles['number_item']))
    story.append(Paragraph("2. 廣告監控／維護／優化：定期監控成效數據，進行必要之調整與優化。", styles['number_item']))
    story.append(Paragraph("3. 簡易週報：每週提供廣告成效摘要及下週優化方向。", styles['number_item']))

    story.append(Spacer(1, 5))
    story.append(Paragraph("<b>二、非固定工作項目（視實際狀況提供）</b>", styles['normal_no_indent']))
    story.append(Paragraph("1. 廣告素材建議：乙方得依投放成效、競品與市場狀況，提供素材與文案方向建議。", styles['number_item']))
    story.append(Paragraph("2. 到達頁面優化建議：於轉換成效異常或下降時，提供頁面優化方向。", styles['number_item']))

    # 第三條：服務範圍與限制
    story.append(Paragraph("<b>第三條　服務範圍與限制</b>", styles['heading']))
    story.append(Paragraph("1. 本服務範圍以 Meta（Facebook／Instagram）廣告投放為主；若需擴展至其他平台，雙方另行協議。", styles['number_item']))
    story.append(Paragraph("2. 廣告投放預算由甲方自行支付予廣告平台，不包含於本合約服務費用內。", styles['number_item']))
    story.append(Paragraph("3. 廣告素材（圖片、影片等）之製作原則上由甲方提供，乙方提供方向與建議。", styles['number_item']))
    story.append(Paragraph("4. 甲方應提供必要帳號權限、素材與資訊，以確保服務得以順利執行。", styles['number_item']))

    # 第四條：配合事項（保留你的替代作業語意但不過度暴露）
    story.append(Paragraph("<b>第四條　配合事項與作業方式</b>", styles['heading']))
    story.append(Paragraph("1. 甲方同意配合乙方所需之資料提供、權限設定與必要操作，以確保服務品質。", styles['number_item']))
    story.append(Paragraph("2. 若因平台政策、帳號狀況或其他不可控因素，需改採替代作業方式（例如：由甲方匯出報表供乙方監控），甲方同意合理配合。", styles['number_item']))

    # 第五條：費用與付款方式（翻正：甲方付乙方）
    story.append(Paragraph("<b>第五條　費用與付款方式</b>", styles['heading']))

    if payment_option == "17,000元/月（每月付款）":
        story.append(Paragraph("1. 甲方同意支付乙方服務費用 <b>新台幣壹萬柒仟元整（NT$17,000）／月</b>。", styles['number_item']))
        story.append(Paragraph(f"2. 付款時間：甲方應於每月 {payment_day} 日前支付當月服務費用至乙方指定帳戶。", styles['number_item']))
        story.append(Paragraph(f"3. 首期款項應於合作啟動日（{start_date.strftime('%Y 年 %m 月 %d 日')}）前支付完成。", styles['number_item']))
    else:
        story.append(Paragraph("1. 甲方同意支付乙方服務費用 <b>新台幣肆萬伍仟元整（NT$45,000）／三個月</b>。", styles['number_item']))
        story.append(Paragraph(f"2. 付款時間：甲方應於 {payment_date.strftime('%Y 年 %m 月 %d 日')} 前一次支付完成。", styles['number_item']))

    story.append(Paragraph("3. 逾期付款者，乙方得暫停服務至款項付清為止；因此造成之廣告中斷或成效波動，乙方不負賠償責任。", styles['number_item']))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>乙方指定收款帳戶：</b>", styles['normal_no_indent']))
    story.append(Paragraph(f"銀行：{bank_name}（銀行代碼：{bank_code}）", styles['bank_info']))
    story.append(Paragraph(f"帳號：{account_number}", styles['bank_info']))

    # 第六條：付款方式與稅務責任（不寫死勞報）
    story.append(Paragraph("<b>第六條　付款方式與稅務責任</b>", styles['heading']))
    story.append(Paragraph("1. 乙方為自然人，依法無須開立統一發票。", styles['number_item']))
    story.append(Paragraph("2. 本合約費用之付款方式、帳務處理及相關稅務申報，均由甲方依其自身狀況及相關法令自行決定並負責。", styles['number_item']))
    story.append(Paragraph("3. 甲方得依其帳務或實務需求，選擇是否以勞務報酬方式支付或其他合法方式付款；乙方將於合理需求下配合提供必要之收款或服務文件。", styles['number_item']))
    story.append(Paragraph("4. 乙方不負責判斷、建議或保證任何稅務處理方式之合法性。", styles['number_item']))
    story.append(Paragraph("5. 因甲方之付款方式或稅務處理所生之一切法律或行政責任，概由甲方自行負責。", styles['number_item']))

    # 第七條：成效聲明
    story.append(Paragraph("<b>第七條　成效聲明與免責</b>", styles['heading']))
    story.append(Paragraph("1. 乙方將盡專業所能優化廣告成效，但廣告投放成效受市場環境、競爭狀況、消費者行為、平台演算法等多重因素影響，乙方不保證特定之轉換率、ROAS 或銷售成果。", styles['number_item']))
    story.append(Paragraph("2. 因平台政策變更、帳號異常、不可抗力因素等非乙方可控原因導致之廣告中斷或成效下降，乙方不負賠償責任。", styles['number_item']))
    story.append(Paragraph("3. 甲方提供之素材、商品或服務如違反廣告平台政策或法令規定，導致廣告被拒絕或帳號受處分，乙方不負相關責任。", styles['number_item']))

    # 第八條：保密
    story.append(Paragraph("<b>第八條　保密條款</b>", styles['heading']))
    story.append(Paragraph("1. 合作期間所涉及之商業資訊、廣告數據、行銷策略及客戶資料等，均屬機密資訊，僅得用於本合作目的。", styles['number_item']))
    story.append(Paragraph("2. 本保密義務於合約終止後仍持續有效 2 年。", styles['number_item']))

    # 第九條：智慧財產權
    story.append(Paragraph("<b>第九條　智慧財產權</b>", styles['heading']))
    story.append(Paragraph("1. 乙方提供之廣告文案、策略建議、報告等成果，於甲方付清全部款項後，甲方得於本案範圍內使用。", styles['number_item']))
    story.append(Paragraph("2. 甲方提供之品牌素材、商標、圖片等，其權利仍歸甲方所有。", styles['number_item']))

    # 第十條：合約終止
    story.append(Paragraph("<b>第十條　合約終止</b>", styles['heading']))
    story.append(Paragraph("1. 任一方如欲提前終止本合約，應於終止日前 14 日以書面（含電子郵件、通訊軟體訊息）通知他方。", styles['number_item']))
    if payment_option == "17,000元/月（每月付款）":
        story.append(Paragraph("2. 月付方案：已支付之當期費用不予退還；甲方仍可於當期內使用既定服務至當期結束。", styles['number_item']))
    else:
    story.append(Paragraph(
        "2. 季付方案屬優惠性質之預付服務費，一經支付後即不予退還。即使甲方於合約期間內提前終止或未使用完畢服務內容，亦同；惟因乙方重大違約致服務無法履行者，不在此限。",
        styles['number_item']))


    # 第十一條：通知方式
    story.append(Paragraph("<b>第十一條　通知方式</b>", styles['heading']))
    story.append(Paragraph("本合約相關通知，得以電子郵件、LINE、Messenger 或其他雙方約定之通訊方式為之，於發送時即生效力。", styles['normal']))

    # 第十二條：合約變更
    story.append(Paragraph("<b>第十二條　合約變更</b>", styles['heading']))
    story.append(Paragraph("本合約之任何修改或補充，應經雙方書面同意後始生效力。", styles['normal']))

    # 第十三條：不可抗力
    story.append(Paragraph("<b>第十三條　不可抗力</b>", styles['heading']))
    story.append(Paragraph("因天災、戰爭、政府行為、網路中斷、平台系統異常或其他不可抗力因素，致任一方無法履行本合約義務時，該方不負違約責任；惟應儘速通知並於事由消滅後恢復履行。", styles['normal']))

    # 第十四條：爭議處理
    story.append(Paragraph("<b>第十四條　爭議處理</b>", styles['heading']))
    story.append(Paragraph("本合約之解釋與適用，以中華民國法律為準據法。雙方如有爭議，應先行協商；協商不成以臺灣臺北地方法院為第一審管轄法院。", styles['normal']))

    story.append(Spacer(1, 18))

    # 簽署欄
    story.append(Paragraph("<b>立合約書人</b>", styles['heading']))
    story.append(Spacer(1, 8))

    signature_data = [
        ['甲方（委託暨付款方）', '', '乙方（服務執行者）'],
        ['', '', ''],
        [f'名稱：{party_a_name}', '', f'名稱：{party_b_name}'],
        ['', '', ''],
        ['簽名：___________________', '', '簽名：___________________'],
        ['', '', ''],
        ['日期：_____ 年 ___ 月 ___ 日', '', '日期：_____ 年 ___ 月 ___ 日'],
    ]

    signature_table = Table(signature_data, colWidths=[6.5 * cm, 2 * cm, 6.5 * cm])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.lightgrey),
        ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.lightgrey),
    ]))
    story.append(signature_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# =========================================================
# 9) 生成按鈕：存 session_state（下載後不消失）
# =========================================================
st.header("✅ 生成")

if st.button("📄 生成合約內容", type="primary", use_container_width=True):
    if not party_a_name.strip():
        st.error("請輸入甲方名稱（委託暨付款方）")
    elif not party_b_name.strip():
        st.error("請輸入乙方名稱（服務執行者）")
    elif not bank_code.strip() or not account_number.strip():
        st.error("請填寫乙方收款資訊（銀行代碼與帳號）")
    else:
        # 客戶回傳訊息（甲方回傳給你）
        if payment_option == "17,000元/月（每月付款）":
            client_message = f"""您好，我已確認廣告投放服務內容，以下是本次合約資訊：

【甲方（委託暨付款方）】{party_a_name}
【乙方（服務執行者）】{party_b_name}
【付款方案】17,000元/月（每月付款）
【合作啟動日期】{start_date.strftime('%Y年%m月%d日')}
【每月付款日】每月 {payment_day} 日

請確認以上資訊，謝謝！"""
        else:
            client_message = f"""您好，我已確認廣告投放服務內容，以下是本次合約資訊：

【甲方（委託暨付款方）】{party_a_name}
【乙方（服務執行者）】{party_b_name}
【付款方案】45,000元/三個月（一次付款）
【合作啟動日期】{start_date.strftime('%Y年%m月%d日')}
【付款日期】{payment_date.strftime('%Y年%m月%d日')}

請確認以上資訊，謝謝！"""

        payment_message = f"""Hi～以下為乙方收款帳戶資訊：

銀行：{bank_name}（{bank_code}）
帳號：{account_number}

💡提醒：轉帳前請再次確認帳號與金額正確。"""

        pdf_bytes = generate_pdf_bytes(
            party_a_name=party_a_name,
            party_b_name=party_b_name,
            bank_name=bank_name,
            bank_code=bank_code,
            account_number=account_number,
            payment_option=payment_option,
            start_date=start_date,
            payment_day=payment_day,
            payment_date=payment_date
        )

        st.session_state.client_message = client_message
        st.session_state.payment_message = payment_message
        st.session_state.pdf_bytes = pdf_bytes
        st.session_state.generated = True
        st.session_state.last_party_a_name = party_a_name

        st.success("✅ 已生成完成（下載 PDF 後內容不會消失）")


# =========================================================
# 10) 顯示區（永遠從 session_state 讀）
# =========================================================
if st.session_state.generated:
    st.markdown("---")
    st.subheader("📤 甲方回傳確認訊息（可複製）")
    st.text_area("回傳訊息", value=st.session_state.client_message, height=220)

    st.subheader("💳 乙方收款訊息（可複製）")
    st.text_area("收款訊息", value=st.session_state.payment_message, height=140)

    st.subheader("📥 下載合約 PDF")
    filename = f"廣告投放服務合約_{st.session_state.last_party_a_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    st.download_button(
        label="⬇️ 下載合約 PDF",
        data=st.session_state.pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True,
        key="download_contract_pdf"
    )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 清空本次結果（換下一位）", use_container_width=True):
            st.session_state.generated = False
            st.session_state.client_message = ""
            st.session_state.payment_message = ""
            st.session_state.pdf_bytes = b""
            st.session_state.last_party_a_name = ""
            st.rerun()
    with col2:
        st.caption("清空只影響畫面，不影響程式碼與設定。")

st.markdown("---")
st.caption("如有任何問題，請隨時與我聯繫。")
