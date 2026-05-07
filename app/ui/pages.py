from fastapi.responses import HTMLResponse

# ================= BASE UI =================
def base_page(title, body):
    return HTMLResponse(f"""
<html>
<head>
<title>{title}</title>

<style>
body {{
    margin:0;
    font-family: Arial, sans-serif;

    /* 🌈 HAPPY GRADIENT BACKGROUND */
    background: linear-gradient(135deg, #0ea5e9, #6366f1, #22c55e);
    background-size: 300% 300%;
    animation: bg 12s ease infinite;

    color: #0f172a;
}}

@keyframes bg {{
    0% {{background-position:0% 50%;}}
    50% {{background-position:100% 50%;}}
    100% {{background-position:0% 50%;}}
}}

.header {{
    padding: 16px 24px;
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(0,0,0,0.05);
    font-weight: bold;
}}

.container {{
    max-width: 900px;
    margin: 30px auto;
    padding: 20px;
}}

.card {{
    background: rgba(255,255,255,0.92);
    padding: 20px;
    border-radius: 18px;
    margin-bottom: 20px;

    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    backdrop-filter: blur(10px);
}}

h2, h3 {{
    color: #1e293b;
}}

input, select {{
    padding: 10px;
    margin: 6px 0;
    width: 100%;
    border-radius: 10px;
    border: 1px solid #cbd5e1;
    background: white;
    color: #0f172a;
    outline: none;
}}

button {{
    padding: 10px 14px;
    margin-top: 10px;
    border: none;
    border-radius: 10px;

    background: linear-gradient(90deg, #38bdf8, #6366f1);
    color: white;

    cursor: pointer;
    font-weight: bold;
    transition: 0.2s;
}}

button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(99,102,241,0.4);
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

td, th {{
    padding: 12px;
    border-bottom: 1px solid #e2e8f0;
    text-align: left;
}}

tr:hover {{
    background: #f1f5f9;
}}

.success {{
    background: linear-gradient(90deg, #22c55e, #16a34a);
}}

.danger {{
    background: linear-gradient(90deg, #ef4444, #dc2626);
}}

.small {{
    font-size: 12px;
    opacity: 0.7;
}}
</style>

</head>

<body>

<div class="header">
    <div>☁️ <b>CloudExam System</b></div>
    <div class="small">{title}</div>
</div>

<div class="container">
{body}
</div>

</body>
</html>
""")


# ================= LOGIN =================
def login_page():
    return base_page("Login", """
<div class="card">
<h2>Login</h2>

<input id="username" placeholder="Username">
<input id="password" type="password" placeholder="Password">

<button onclick="login()">Login</button>
</div>

<script>
async function login(){
    const d = new FormData();
    d.append("username", username.value);
    d.append("password", password.value);

    const r = await fetch("/login", {method:"POST", body:d});

    if(!r.ok){
        alert("Invalid credentials");
        return;
    }

    const j = await r.json();
    localStorage.setItem("token", j.access_token);
    localStorage.setItem("role", j.role);

    location = j.role === "teacher" ? "/teacher" : "/student";
}
</script>
""")


# ================= REGISTER =================
def register_page():
    return base_page("Register", """
<div class="card">
<h2>Create Account</h2>

<input id="username" placeholder="Username">
<input id="password" type="password" placeholder="Password">

<select id="role">
    <option value="student">Student</option>
    <option value="teacher">Teacher</option>
</select>

<button onclick="register()">Register</button>
</div>

<script>
async function register(){
    const d = new FormData();
    d.append("username", username.value);
    d.append("password", password.value);
    d.append("role", role.value);

    const r = await fetch("/register", {method:"POST", body:d});

    if(!r.ok){
        alert("Registration failed");
        return;
    }

    location = "/login";
}
</script>
""")


# ================= SAFE FETCH =================
SAFE_FETCH = """
async function safeFetch(url, options={}){
    const token = localStorage.getItem("token");

    if(!token){
        alert("Login required");
        location="/login";
        return null;
    }

    options.headers = options.headers || {};
    options.headers["Authorization"] = "Bearer " + token;

    const r = await fetch(url, options);

    if(r.status === 401){
        alert("Session expired");
        localStorage.clear();
        location="/login";
        return null;
    }

    return r;
}
"""


# ================= TEACHER =================
def teacher_page():
    return base_page("Teacher Dashboard", f"""
<div class="card">
<h2>Teacher Panel</h2>

<input type="file" id="fileInput">
<button onclick="upload()">Upload</button>
</div>

<div class="card">
<h3>All Files</h3>
<table>
<tbody id="table"></tbody>
</table>
</div>

<script>
{SAFE_FETCH}

async function load(){{
    const r = await safeFetch("/all-files");
    if(!r) return;

    const data = await r.json();
    table.innerHTML = "";

    data.forEach(f => {{
        table.innerHTML += `
        <tr>
            <td>${{f.filename}}</td>
            <td>
                <button class="success" onclick="downloadFile('${{f.file_id}}','${{f.filename}}')">Download</button>
                <button class="danger" onclick="deleteFile('${{f.file_id}}')">Delete</button>
            </td>
        </tr>`;
    }});
}}

async function upload(){{
    const f = fileInput.files[0];
    if(!f) return alert("Select file");

    const d = new FormData();
    d.append("file", f);

    const r = await safeFetch("/upload", {{
        method:"POST",
        body:d
    }});

    if(r) load();
}}

async function downloadFile(id,name){{
    const r = await safeFetch("/download?file_id="+id);
    if(!r) return;

    const blob = await r.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
}}

async function deleteFile(id){{
    await safeFetch("/delete?file_id="+id, {{method:"DELETE"}});
    load();
}}

load();
</script>
""")


# ================= STUDENT =================
def student_page():
    return base_page("Student Dashboard", f"""
<div class="card">
<h2>Student Panel</h2>

<input type="file" id="fileInput">
<button onclick="upload()">Upload</button>
</div>

<div class="card">
<h3>My Files</h3>
<table>
<tbody id="table"></tbody>
</table>
</div>

<div class="card">
<h3>Download File</h3>
<input id="filename" placeholder="Enter filename">
<button onclick="downloadByName()">Download</button>
</div>

<script>
{SAFE_FETCH}

async function load(){{
    const r = await safeFetch("/my-files");
    if(!r) return;

    const data = await r.json();
    table.innerHTML = "";

    data.forEach(f => {{
        table.innerHTML += `
        <tr>
            <td>${{f.filename}}</td>
            <td>
                <button class="danger" onclick="deleteFile('${{f.file_id}}')">Delete</button>
            </td>
        </tr>`;
    }});
}}

async function upload(){{
    const f = fileInput.files[0];
    if(!f) return alert("Select file");

    const d = new FormData();
    d.append("file", f);

    const r = await safeFetch("/upload", {{
        method:"POST",
        body:d
    }});

    if(r) load();
}}

async function downloadByName(){{
    const name = filename.value;

    const r = await safeFetch("/download-by-name?filename="+name);
    if(!r) return;

    const blob = await r.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
}}

async function deleteFile(id){{
    await safeFetch("/delete?file_id="+id, {{method:"DELETE"}});
    load();
}}

load();
</script>
""")