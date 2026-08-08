import os
import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(page_title="Employee Login Portal", page_icon="🔐")

# --- Language Translations Dictionary ---
translations = {
    "English": {
        "title": "🔐 Employee Login Portal",
        "subtitle": "Please enter your National ID to proceed.",
        "admin_header": "Admin Control Panel",
        "admin_pass_label": "Enter Admin Password:",
        "admin_pass_btn": "Unlock Admin Panel",
        "admin_access_denied": "Incorrect Admin Password.",
        "admin_panel_unlocked": "Admin Panel Unlocked Successfully!",
        "upload_label": "Upload Employees Excel File",
        "remove_btn": "Remove Excel Sheet (Logout Everyone)",
        "upload_success": (
            "Excel file uploaded successfully! Employees can now register."
        ),
        "remove_success": "Excel file removed. All active sessions logged out.",
        "upload_warning": (
            "⚠️ Employee database not uploaded yet. Please ask the admin to"
            " upload the Excel file from the sidebar."
        ),
        "input_label": "National ID (الرقم القومي):",
        "password_input_label": "Password (كلمة المرور):",
        "new_password_label": "Create Your Password (أنشئ كلمة المرور):",
        "confirm_password_label": "Confirm Password (تأكيد كلمة المرور):",
        "register_btn": "Register & Request Approval",
        "login_btn": "Login",
        "logout_btn": "Logout",
        "empty_input": "Please fill in all required fields.",
        "pass_mismatch": "Passwords do not match. Please try again.",
        "pass_taken": (
            "⚠️ This password is already taken by another employee. Please"
            " choose a different one."
        ),
        "error_id": "Incorrect National ID. Please check and try again.",
        "error_login": "Incorrect Password. Please check and try again.",
        "pending_approval": (
            "⏳ Your account is registered, but **waiting for Admin approval**."
            " Please contact your administrator to unlock your account."
        ),
        "register_success": (
            "Password created successfully! Your account is now pending admin"
            " approval."
        ),
        "error_read": "Error reading file: {error}",
        "dashboard_title": "Detailed Payroll & Salary Breakdown",
        "welcome_banner": "Welcome, {name}!",
        "id_display": "National ID:",
        "table_col_key": "Field / Column",
        "table_col_val": "Value",
        "admin_approvals_header": "👥 Employee Approvals",
        "approve_btn": "Approve",
        "revoke_btn": "Revoke Access",
    },
    "العربية": {
        "title": "🔐 بوابة تسجيل دخول الموظفين",
        "subtitle": "الرجاء إدخال الرقم القومي للمتابعة.",
        "admin_header": "لوحة تحكم المسؤول (Admin)",
        "admin_pass_label": "أدخل كلمة مرور المسؤول:",
        "admin_pass_btn": "فتح لوحة المسؤول",
        "admin_access_denied": "كلمة مرور المسؤول غير صحيحة.",
        "admin_panel_unlocked": "تم فتح لوحة المسؤول بنجاح!",
        "upload_label": "رفع ملف الـ Excel للموظفين",
        "remove_btn": "حذف ملف الـ Excel (تسجيل خروج الجميع)",
        "upload_success": (
            "تم رفع ملف الـ Excel بنجاح! يمكن للموظفين التسجيل الآن."
        ),
        "remove_success": "تم حذف الملف وتسجيل خروج جميع الجلسات النشطة.",
        "upload_warning": (
            "⚠️ لم يتم رفع قاعدة بيانات الموظفين بعد. يرجى من المسؤول رفع ملف الـ"
            " Excel من القائمة الجانبية."
        ),
        "input_label": "الرقم القومي (National ID):",
        "password_input_label": "كلمة المرور (Password):",
        "new_password_label": "أنشئ كلمة المرور الخاصة بك:",
        "confirm_password_label": "تأكيد كلمة المرور:",
        "register_btn": "التسجيل وطلب الموافقة",
        "login_btn": "تسجيل الدخول",
        "logout_btn": "تسجيل الخروج",
        "empty_input": "الرجاء ملء جميع الحقول المطلوبة.",
        "pass_mismatch": "كلمتا المرور غير متطابقتين. يرجى المحاولة مرة أخرى.",
        "pass_taken": (
            "⚠️ كلمة المرور هذه مستخدمة من قبل موظف آخر. اختر كلمة مرور فريدة."
        ),
        "error_id": "الرقم القومي غير صحيح. يرجى التحقق والمحاولة مرة أخرى.",
        "error_login": "كلمة المرور غير صحيحة. يرجى التحقق.",
        "pending_approval": (
            "⏳ حسابك مسجل ولكن **في انتظار موافقة المسؤول (Admin)**. يرجى التواصل"
            " مع الإدارة لتفعيل حسابك."
        ),
        "register_success": (
            "تم إنشاء كلمة المرور بنجاح! حسابك في انتظار موافقة المسؤول الآن."
        ),
        "error_read": "خطأ في قراءة الملف: {error}",
        "dashboard_title": "تفصيل مفردات الراتب والبيانات المالية",
        "welcome_banner": "أهلاً بك يا {name}!",
        "id_display": "الرقم القومي:",
        "table_col_key": "الحقل / العمود",
        "table_col_val": "القيمة",
        "admin_approvals_header": "👥 موافقة حسابات الموظفين",
        "approve_btn": "موافقة",
        "revoke_btn": "إلغاء التفعيل",
    },
}

# --- Language Switcher in Sidebar ---
st.sidebar.title("🌐 Language / اللغة")
selected_lang = st.sidebar.selectbox("Choose Language", ["العربية", "English"])
t = translations[selected_lang]

SHARED_FILE = "shared_payroll.xlsx"
ADMIN_PASSWORD = "Mirage_Payroll_Secured_2026!#$xK9"

# Initialize session states
if "logged_in_user" not in st.session_state:
  st.session_state.logged_in_user = None
if "logged_in_id" not in st.session_state:
  st.session_state.logged_in_id = None
if "employee_row_data" not in st.session_state:
  st.session_state.employee_row_data = None
if "admin_authenticated" not in st.session_state:
  st.session_state.admin_authenticated = False


# --- Helper to load dataframe safely ---
def load_excel_df():
  if not os.path.exists(SHARED_FILE):
    return None
  df = pd.read_excel(SHARED_FILE)
  df.columns = df.columns.str.strip()
  if "Password" not in df.columns:
    df["Password"] = ""
  if "Status" not in df.columns:
    df["Status"] = "Pending"
  return df


# --- Admin Section (Sidebar with Password Protection) ---
st.sidebar.markdown("---")
st.sidebar.header(t["admin_header"])

if not st.session_state.admin_authenticated:
  admin_pass_input = st.sidebar.text_input(
      t["admin_pass_label"], type="password"
  )
  if st.sidebar.button(t["admin_pass_btn"]):
    if admin_pass_input == ADMIN_PASSWORD:
      st.session_state.admin_authenticated = True
      st.sidebar.success(t["admin_panel_unlocked"])
      st.rerun()
    else:
      st.sidebar.error(t["admin_access_denied"])
else:
  uploaded_file = st.sidebar.file_uploader(t["upload_label"], type=["xlsx", "xls"])

  if uploaded_file is not None:
    try:
      df_upload = pd.read_excel(uploaded_file)
      df_upload.columns = df_upload.columns.str.strip()
      df_upload["Password"] = ""
      df_upload["Status"] = "Pending"
      df_upload.to_excel(SHARED_FILE, index=False)
      st.sidebar.success(t["upload_success"])
      st.rerun()
    except Exception as e:
      st.sidebar.error(t["error_read"].format(error=e))

  if os.path.exists(SHARED_FILE):
    st.sidebar.markdown("---")
    st.sidebar.subheader(t["admin_approvals_header"])
    df_admin = load_excel_df()
    if df_admin is not None:
      for idx, row in df_admin.iterrows():
        name = row.get("الاسم", f"Employee {idx}")
        status = str(row.get("Status", "Pending")).strip()
        has_pass = (
            str(row.get("Password", "")).strip() not in ["", "nan", "None"]
        )

        if has_pass:
          col_a, col_b = st.sidebar.columns([2, 1])
          col_a.write(f"**{name}** ({status})")
          if status.lower() == "approved":
            if col_b.button(t["revoke_btn"], key=f"rev_{idx}"):
              df_admin.at[idx, "Status"] = "Pending"
              df_admin.to_excel(SHARED_FILE, index=False)
              st.rerun()
          else:
            if col_b.button(t["approve_btn"], key=f"app_{idx}"):
              df_admin.at[idx, "Status"] = "Approved"
              df_admin.to_excel(SHARED_FILE, index=False)
              st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button(t["remove_btn"]):
      os.remove(SHARED_FILE)
      st.sidebar.success(t["remove_success"])
      st.rerun()

  if st.sidebar.button("Lock Admin Panel / قفل لوحة المسؤول"):
    st.session_state.admin_authenticated = False
    st.rerun()

# Check globally if the shared file exists
file_exists = os.path.exists(SHARED_FILE)

if not file_exists and st.session_state.logged_in_user is not None:
  st.session_state.logged_in_user = None
  st.session_state.logged_in_id = None
  st.session_state.employee_row_data = None
  st.rerun()

# --- Main Page Layout ---
st.title(t["title"])

if st.session_state.logged_in_user:
  st.success(t["welcome_banner"].format(name=st.session_state.logged_in_user))

  st.markdown(f"### 📋 {t['dashboard_title']}")
  st.info(
      f"**{t['id_display']}**"
      f" `{str(st.session_state.logged_in_id).strip()}`"
  )

  if st.session_state.employee_row_data is not None:
    row_data = st.session_state.employee_row_data

    table_data = []
    for col_name, val in row_data.items():
      if str(col_name).strip().lower() in ["password", "status", "كلمة المرور"]:
        continue

      display_val = val
      if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan":
        display_val = 0
      table_data.append(
          {t["table_col_key"]: str(col_name), t["table_col_val"]: display_val}
      )

    df_display = pd.DataFrame(table_data)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

  st.markdown("---")
  if st.button(t["logout_btn"]):
    st.session_state.logged_in_user = None
    st.session_state.logged_in_id = None
    st.session_state.employee_row_data = None
    st.rerun()

else:
  st.write(t["subtitle"])

  if not file_exists:
    st.warning(t["upload_warning"])
  else:
    try:
      df = load_excel_df()
      national_id_input = st.text_input(t["input_label"])

      if national_id_input:
        matched = df[
            df["الرقم القومي"].astype(str).str.strip()
            == national_id_input.strip()
        ]

        if not matched.empty:
          idx = matched.index[0]
          current_pass = str(matched.loc[idx, "Password"]).strip()
          status = str(matched.loc[idx, "Status"]).strip().lower()

          # SCENARIO 1: No password created yet -> ONLY show ID box and Registration inputs
          if current_pass == "" or current_pass.lower() == "nan":
            st.info(
                "✨ First time here? Please create a secure, unique password"
                " for your account."
            )
            new_pass = st.text_input(
                t["new_password_label"], type="password", key="new_p"
            )
            confirm_pass = st.text_input(
                t["confirm_password_label"], type="password", key="conf_p"
            )

            if st.button(t["register_btn"]):
              if not new_pass or not confirm_pass:
                st.warning(t["empty_input"])
              elif new_pass != confirm_pass:
                st.error(t["pass_mismatch"])
              else:
                existing_passes = df["Password"].astype(str).str.strip().tolist()
                if new_pass.strip() in existing_passes:
                  st.error(t["pass_taken"])
                else:
                  df.at[idx, "Password"] = new_pass.strip()
                  df.at[idx, "Status"] = "Pending"
                  df.to_excel(SHARED_FILE, index=False)
                  st.success(t["register_success"])
                  st.rerun()

          # SCENARIO 2: Password exists, but NOT approved yet -> Block access completely
          elif status != "approved":
            password_input = st.text_input(
                t["password_input_label"], type="password", key="login_p"
            )
            if st.button(t["login_btn"]):
              if password_input.strip() == current_pass:
                st.warning(t["pending_approval"])
              else:
                st.error(t["error_login"])

          # SCENARIO 3: Password exists AND Approved -> Allow login
          else:
            password_input = st.text_input(
                t["password_input_label"], type="password", key="login_p"
            )
            if st.button(t["login_btn"]):
              if not password_input:
                st.warning(t["empty_input"])
              elif password_input.strip() == current_pass:
                st.session_state.logged_in_user = matched.loc[idx, "الاسم"]
                st.session_state.logged_in_id = national_id_input.strip()
                st.session_state.employee_row_data = matched.loc[idx].to_dict()
                st.rerun()
              else:
                st.error(t["error_login"])
        else:
          if st.button(t["login_btn"]):
            st.error(t["error_id"])

    except Exception as e:
      st.error(t["error_read"].format(error=e))
