import streamlit as st
from datetime import datetime, timedelta
import io
import os

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# =========================
# 0) 基本設定（請填）
# =========================
PROVIDER_NAME = ""  # 甲方名稱（你的姓名）
BANK_NAME = "中國信託商業銀行"
BANK_CODE = "822"
ACCOUNT_NUMBER = "783540208870"

FONT_PATH = "assets/fonts/NotoSansTC-Regular.ttf"  # ✅ 方案 B：嵌字型
FONT_NAME = "NotoSansTC"


# =========================
# 1) Streamlit page
# =========================
st.set_page_config(
    page_title="廣告投放服務選擇",
    page_icon="📋",
    layout="centered"
)

st.title("📋 廣告投放服務內容")
st.markdown("---")


# =========================
# 2) Session State（避免下載後清空）
# =========================
if "generated" not in st.session_state:
    st.session_state.generated = False
    st.session_state.client_message = ""
    st.session_state.payment_message = ""
    st.session_state.pdf_bytes = b""
    st.session_state.last_client_name = ""


# =========================
# 3) 字型載入（嵌入 TTF）
# =========================
def ensure_font_loaded():
    if not os.path.exists(FONT_PATH):
        st.error(f"找不到字型檔：{FONT_PATH}\n\n請把 NotoSansTC-Regular.ttf 放到該路徑後再試。")
        st.stop()
    # 避免重複 register
    try:
        pdfmetrics.getFont(FONT_NAME)
    except KeyError:
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))


# =========================
# 4) UI：服務內容
# =========================
st.header("服務內容說明")

st.subheader("✅ 固定工作")
st.markdown("""
- **廣告上架**
- **廣告監控 / 維護 / 優化**
- **簡易週報**（成果與優化方向）
""")

st.subheader("📌 非固定工作")
st.markdown("""
- **廣告素材建議**
  - 依成效、競品、市場研究提出素材方向
  - 提供廣告文案 / 圖片素材文字建議供調整
- **到達頁面優化建議**
  - 監控轉換成效
  - 轉換率異常或下降時提供優化建議
""")

st.warning("""
📌 **提醒**
- 甲方以自然人身分提供服務，不開立統一發票。
- 付款方式、帳務與稅務申報由乙方依自身狀況與法規自行決定並負責，甲方不提供稅務判斷。
""")

st.markdown("---")


# =========================
# 5) UI：收費方式
# =========================
st.header("💰 收費方式選擇")

payment_option = st.radio(
    "請選擇您偏好的付款方式：",
    options=[
        "17,000元/月（每月付款）",
        "45,000元/三個月（一次付款）"
    ],
    index=0
)

st.markdown("---")


# =========================
# 6) UI：合作時間
# =========================
st.header("📅 合作時間設定")

default_start = datetime.now().date() + timedelta(days=7)
start_date = st.date_input(
    "合作啟動日期",
    value=default_start,
    min_value=datetime.now().date()
)

payment_day = None
payment_date = None
total_amount_text = ""
contract_type = ""

if payment_option == "17,000元/月（每月付款）":
    st.subheader("每月付款設定")
    payment_day = st.slider(
        "每月付款日（例如：每月 5 號）",
        min_value=1,
        max_value=28,
        value=5,
        help="選擇每個月的付款日期"
    )
    total_amount_text = "NT$17,000／月"
    contract_type = "月付方案"
else:
    st.subheader("一次付款設定")
    default_payment = start_date - timedelta(days=3)
    if default_payment < datetime.now().date():
        default_payment = datetime.now().date()

    payment_date = st.date_input(
        "付款日期（建議於合作啟動前完成付款）",
        value=default_payment,
        min_value=datetime.now().date(),
        max_value=start_date
    )
    total_amount_text = "NT$45,000／三個月"
    contract_type = "季付方案"


st.markdown("---")


# =========================
# 7) UI：客戶資訊
# =========================
st.header("📝 客戶資訊")
client_name = st.text_input("客戶名稱/公司名稱", placeholder="請輸入您的名稱或公司名稱")

st.markdown("---")


# =========================
# 8) PDF 產生（回傳 bytes）
# =========================
def generate_pdf_bytes(
    client_name: str,
    start_date,
    payment_option: str,
    payment_day: int | None,
    payment_date,
):
    ensure_font_loaded()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = {
        'title': ParagraphStyle(
            'Title',
            fontName=FONT_NAME,
            fontSize=18,
            alignment=1,
            spaceAfter=20,
            spaceBefore=5
        ),
        'heading': ParagraphStyle(
            'Heading',
            fontName=FONT_NAME,
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6
        ),
        'party': ParagraphStyle(
            'Party',
            fontName=FONT_NAME,
            fontSize=11,
            spaceBefore=3,
            spaceAfter=3,
            leading=16
        ),
        'normal': ParagraphStyle(
            'Normal',
            fontName=FONT_NAME,
            fontSize=10,
            spaceBefore=3,
            spaceAfter=3,
            leading=16,
            firstLineIndent=20
        ),
        'normal_no_indent': ParagraphStyle(
            'NormalNoIndent',
            fontName=FONT_NAME,
            fontSize=10,
            spaceBefore=3,
            spaceAfter=3,
            leading=16
        ),
        'number_item': ParagraphStyle(
            'NumberItem',
            fontName=FONT_NAME,
            fontSize=10,
            leftIndent=15,
            spaceBefore=2,
            spaceAfter=2,
            leading=14
        ),
        'bank_info': ParagraphStyle(
            'BankInfo',
            fontName=FONT_NAME,
            fontSize=10,
            leftIndent=15,
            spaceBefore=2,
            spaceAfter=2,
            leading=14
        )
    }

    story = []
    story.append(Paragraph("<b>廣告投放服務合約書</b>", styles['title']))

    # 合約期間（用 30/90 天：你的原始版語意一致，且簡單）
    if payment_option == "17,000元/月（每月付款）":
        contract_end = start_date + timedelta(days=30)
        contract_period_text = (
            f"自 {start_date.strftime('%Y 年 %m 月 %d 日')} 起至 "
            f"{contract_end.strftime('%Y 年 %m 月 %d 日')} 止，共 1 個月。"
            "届期如雙方無異議，則本合約自動續行 1 個月，以此類推。"
        )
    else:
        contract_end = start_date + timedelta(days=90)
        contract_period_text = (
            f"自 {start_date.strftime('%Y 年 %m 月 %d 日')} 起至 "
            f"{contract_end.strftime('%Y 年 %m 月 %d 日')} 止，共 3 個月。"
            "届期如雙方有意續約，應於届滿前 7 日另行協議。"
        )

    # 甲乙方
    story.append(Paragraph(f"<b>甲方（服務提供者）：</b>{PROVIDER_NAME}", styles['party']))
    story.append(Paragraph(f"<b>乙方（委託客戶）：</b>{client_name}", styles['party']))
    story.append(Spacer(1, 8))

    # 前言
    story.append(Paragraph(
        "茲因乙方委託甲方提供數位廣告投放服務，雙方本於誠信原則，同意訂立本合約，並共同遵守下列條款：",
        styles['normal']
    ))

    # 第一條
    story.append(Paragraph("<b>第一條　合約期間</b>", styles['heading']))
    story.append(Paragraph(contract_period_text, styles['normal']))

    # 第二條
    story.append(Paragraph("<b>第二條　服務內容</b>", styles['heading']))
    story.append(Paragraph("甲方同意為乙方提供以下廣告投放服務：", styles['normal_no_indent']))

    story.append(Paragraph("<b>一、固定工作項目</b>", styles['normal_no_indent']))
    story.append(Paragraph("1. 廣告上架：依乙方需求於指定平台建立並上架廣告活動。", styles['number_item']))
    story.append(Paragraph("2. 廣告監控／維護／優化：定期監控成效數據，進行必要之調整與優化。", styles['number_item']))
    story.append(Paragraph("3. 簡易週報：每週提供廣告成效摘要及下週優化方向。", styles['number_item']))

    story.append(Spacer(1, 5))
    story.append(Paragraph("<b>二、非固定工作項目（視實際狀況提供）</b>", styles['normal_no_indent']))
    story.append(Paragraph("1. 廣告素材建議：依投放成效、競品與市場狀況，提供素材與文案方向建議。", styles['number_item']))
    story.append(Paragraph("2. 到達頁面優化建議：於轉換成效異常或下降時，提供頁面優化方向。", styles['number_item']))

    # 第三條
    story.append(Paragraph("<b>第三條　服務範圍與限制</b>", styles['heading']))
    story.append(Paragraph("1. 本服務範圍以 Meta（Facebook／Instagram）廣告投放為主；若需擴展至其他平台，雙方另行協議。", styles['number_item']))
    story.append(Paragraph("2. 廣告投放預算由乙方自行支付予廣告平台，不包含於本合約服務費用內。", styles['number_item']))
    story.append(Paragraph("3. 廣告素材（圖片、影片等）之製作由乙方負責，甲方提供方向與建議。", styles['number_item']))
    story.append(Paragraph("4. 乙方應提供必要帳號權限與素材資訊，以確保服務得以順利執行。", styles['number_item']))

    # 第四條
    story.append(Paragraph("<b>第四條　現況說明與配合事項</b>", styles['heading']))
    story.append(Paragraph(
        "目前甲方 Facebook 個人帳號可能因不可控因素影響日常操作，雙方同意採取以下替代作業方式（如有需要）：",
        styles['normal_no_indent']
    ))
    story.append(Paragraph("1. 乙方依甲方指示匯出廣告數據，供甲方進行監控與判斷。", styles['number_item']))
    story.append(Paragraph("2. 若需調整後台，雙方得以線上方式（遠端/通訊）協作完成。", styles['number_item']))
    story.append(Paragraph("3. 乙方同意配合必要之資料提供與操作協作，以確保服務品質。", styles['number_item']))

    # 第五條
    story.append(Paragraph("<b>第五條　費用與付款方式</b>", styles['heading']))
    if payment_option == "17,000元/月（每月付款）":
        story.append(Paragraph("1. 乙方同意支付甲方服務費用 <b>新台幣壹萬柒仟元整（NT$17,000）／月</b>。", styles['number_item']))
        story.append(Paragraph(f"2. 付款時間：乙方應於每月 {payment_day} 日前支付當月服務費用至甲方指定帳戶。", styles['number_item']))
        story.append(Paragraph(f"3. 首期款項應於合作啟動日（{start_date.strftime('%Y 年 %m 月 %d 日')}）前支付完成。", styles['number_item']))
    else:
        story.append(Paragraph("1. 乙方同意支付甲方服務費用 <b>新台幣肆萬伍仟元整（NT$45,000）／三個月</b>。", styles['number_item']))
        story.append(Paragraph(f"2. 付款時間：乙方應於 {payment_date.strftime('%Y 年 %m 月 %d 日')} 前一次支付完成。", styles['number_item']))

    story.append(Paragraph("3. 逾期付款者，甲方得暫停服務至款項付清為止；因此造成之廣告中斷或成效波動，甲方不負賠償責任。", styles['number_item']))

    story.append(Spacer(1, 5))
    story.append(Paragraph("<b>甲方指定收款帳戶：</b>", styles['normal_no_indent']))
    story.append(Paragraph(f"銀行：{BANK_NAME}（銀行代碼：{BANK_CODE}）", styles['bank_info']))
    story.append(Paragraph(f"帳號：{ACCOUNT_NUMBER}", styles['bank_info']))

    # ✅ 第六條（最終版：不寫死勞報）
    story.append(Paragraph("<b>第六條　付款方式與稅務責任</b>", styles['heading']))
    story.append(Paragraph("1. 甲方為自然人，非營業登記之公司或商號，依法無須開立統一發票。", styles['number_item']))
    story.append(Paragraph("2. 本合約服務費用之付款方式、帳務處理及相關稅務申報，均由乙方依其自身狀況及相關法令自行決定並負責。", styles['number_item']))
    story.append(Paragraph("3. 乙方得依其帳務或實務需求，選擇是否以勞務報酬方式支付本合約費用，或以其他合法方式付款。", styles['number_item']))
    story.append(Paragraph("4. 甲方將於乙方合理需求下，配合提供必要之收款或服務相關文件，但不負責判斷、建議或保證任何稅務處理方式之合法性。", styles['number_item']))
    story.append(Paragraph("5. 因乙方之付款方式或稅務處理所生之一切法律或行政責任，概由乙方自行負責，與甲方無涉。", styles['number_item']))

    # 第七條
    story.append(Paragraph("<b>第七條　成效聲明與免責</b>", styles['heading']))
    story.append(Paragraph("1. 甲方將盡專業所能優化廣告成效，但不保證特定之轉換率、ROAS 或銷售成果。", styles['number_item']))
    story.append(Paragraph("2. 因平台政策變更、演算法、帳號異常、不可抗力等非甲方可控原因導致之成效波動，甲方不負賠償責任。", styles['number_item']))
    story.append(Paragraph("3. 乙方提供之素材、商品或服務如違反平台政策或法令，導致廣告被拒或帳號受處分，甲方不負相關責任。", styles['number_item']))

    # 第八條
    story.append(Paragraph("<b>第八條　保密條款</b>", styles['heading']))
    story.append(Paragraph("1. 合作期間涉及之商業資訊、廣告數據、策略及客戶資料等，均屬機密資訊，僅得用於本合作目的。", styles['number_item']))
    story.append(Paragraph("2. 本保密義務於合約終止後仍持續有效 2 年。", styles['number_item']))

    # 第九條
    story.append(Paragraph("<b>第九條　智慧財產權</b>", styles['heading']))
    story.append(Paragraph("1. 甲方提供之廣告文案/策略建議等文件，於乙方付清款項後，乙方得於本案範圍內使用。", styles['number_item']))
    story.append(Paragraph("2. 乙方提供之品牌素材、商標、圖片等，其權利仍歸乙方所有。", styles['number_item']))

    # 第十條（終止：簡化且不自相矛盾）
    story.append(Paragraph("<b>第十條　合約終止</b>", styles['heading']))
    story.append(Paragraph("1. 任一方如欲提前終止本合約，應於終止日前 14 日以書面（含電子郵件、通訊軟體訊息）通知他方。", styles['number_item']))
    if payment_option == "17,000元/月（每月付款）":
        story.append(Paragraph("2. 月付方案：已支付之當期費用不予退還；乙方仍可於當期內使用既定服務至當期結束。", styles['number_item']))
    else:
        story.append(Paragraph("2. 季付方案：如提前終止，雙方得依未服務之完整月數協議退費；不足一個月者得不退還。", styles['number_item']))
    story.append(Paragraph("3. 如因一方重大違約致他方權益受損，受損方得立即終止合約並請求損害賠償。", styles['number_item']))

    # 第十一條～第十四條（保留核心）
    story.append(Paragraph("<b>第十一條　通知方式</b>", styles['heading']))
    story.append(Paragraph("本合約相關通知，得以電子郵件、LINE、Messenger 或其他雙方約定之通訊方式為之，於發送時即生效力。", styles['normal']))

    story.append(Paragraph("<b>第十二條　合約變更</b>", styles['heading']))
    story.append(Paragraph("本合約之任何修改或補充，應經雙方書面同意後始生效力。", styles['normal']))

    story.append(Paragraph("<b>第十三條　不可抗力</b>", styles['heading']))
    story.append(Paragraph("因天災、政府行為、網路中斷、平台系統異常等不可抗力因素，致無法履行義務者，不負違約責任；惟應儘速通知並於事由消滅後恢復履行。", styles['normal']))

    story.append(Paragraph("<b>第十四條　爭議處理</b>", styles['heading']))
    story.append(Paragraph("本合約以中華民國法律為準據法；如有爭議，先行協商，協商不成以臺灣臺北地方法院為第一審管轄法院。", styles['normal']))

    story.append(Spacer(1, 20))

    # 簽署欄
    story.append(Paragraph("<b>立合約書人</b>", styles['heading']))
    story.append(Spacer(1, 8))

    signature_data = [
        ['甲方（服務提供者）', '', '乙方（委託客戶）'],
        ['', '', ''],
        [f'姓名／公司：{PROVIDER_NAME}', '', f'姓名／公司：{client_name}'],
        ['', '', ''],
        ['簽名：___________________', '', '簽名：___________________'],
        ['', '', ''],
        ['日期：_____ 年 ___ 月 ___ 日', '', '日期：_____ 年 ___ 月 ___ 日'],
    ]
    signature_table = Table(signature_data, colWidths=[6.5*cm, 2*cm, 6.5*cm])
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
    return buffer.getvalue()  # ✅ bytes


# =========================
# 9) 生成按鈕（存 session_state）
# =========================
if st.button("📄 生成合約內容", type="primary", use_container_width=True):
    if not client_name.strip():
        st.error("請輸入客戶名稱/公司名稱")
    elif not PROVIDER_NAME.strip():
        st.error("請先在程式上方填入甲方名稱（PROVIDER_NAME）")
    else:
        # 客戶回傳訊息
        if payment_option == "17,000元/月（每月付款）":
            cm = f"""您好，我已確認廣告投放服務內容，以下是我的選擇：

【客戶名稱】{client_name}
【付款方案】17,000元/月（每月付款）
【合作啟動日期】{start_date.strftime('%Y年%m月%d日')}
【每月付款日】每月 {payment_day} 日

請確認以上資訊，謝謝！"""
        else:
            cm = f"""您好，我已確認廣告投放服務內容，以下是我的選擇：

【客戶名稱】{client_name}
【付款方案】45,000元/三個月（一次付款）
【合作啟動日期】{start_date.strftime('%Y年%m月%d日')}
【付款日期】{payment_date.strftime('%Y年%m月%d日')}

請確認以上資訊，謝謝！"""

        # 付款訊息（穩：不放過期連結）
        pm = f"""Hi～請轉到我的銀行帳號

代碼：{BANK_NAME}（{BANK_CODE}）
帳號：{ACCOUNT_NUMBER}

💡提醒您：轉帳前請再次確認帳號與金額正確喔！"""

        # PDF bytes
        pdf_bytes = generate_pdf_bytes(
            client_name=client_name,
            start_date=start_date,
            payment_option=payment_option,
            payment_day=payment_day,
            payment_date=payment_date
        )

        st.session_state.client_message = cm
        st.session_state.payment_message = pm
        st.session_state.pdf_bytes = pdf_bytes
        st.session_state.generated = True
        st.session_state.last_client_name = client_name

        st.success("✅ 已生成合約內容（下載後內容不會消失）")


# =========================
# 10) 顯示區（永遠用 session_state）
# =========================
if st.session_state.generated:
    st.subheader("📤 請複製以下訊息傳給我")
    st.text_area("客戶回傳訊息", value=st.session_state.client_message, height=190)

    st.markdown("---")

    st.subheader("💳 付款資訊（可複製）")
    st.text_area("付款訊息", value=st.session_state.payment_message, height=130)

    st.markdown("---")

    st.subheader("📥 下載合約 PDF")
    filename = f"廣告投放服務合約_{st.session_state.last_client_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    st.download_button(
        label="⬇️ 下載合約 PDF",
        data=st.session_state.pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True,
        key="download_contract_pdf"
    )

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🧹 清空本次結果（換下一位客戶）", use_container_width=True):
            st.session_state.generated = False
            st.session_state.client_message = ""
            st.session_state.payment_message = ""
            st.session_state.pdf_bytes = b""
            st.session_state.last_client_name = ""
            st.rerun()

    with col_b:
        st.caption("（清空只會清畫面，不會影響你的程式碼）")


st.markdown("---")
st.caption("如有任何問題，請隨時與我聯繫。")
