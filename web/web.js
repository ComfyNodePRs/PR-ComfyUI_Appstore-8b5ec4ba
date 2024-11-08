import { api } from "../../../scripts/api.js";
import { app } from "../../../scripts/app.js";
import { $el } from "../../../scripts/ui.js";

const styleElement = document.createElement("style"),
  cssCode =
    "\n    #msgDiv{\n      width:800px;\n      height: 200px;\n      text-align: center;\n      font-size: 30px;\n      display: flex;\n      align-items: center;\n      justify-content: center;\n      padding-bottom: 40px;\n      color: var(--fg-color);\n    }\n    #qrCode{\n      display: block;\n      width:256px;\n      height:256px;\n      border-radius: 10px;\n    }\n    #qrBox{\n      display: block;\n      text-align: center;\n      display:flex;\n      flex-wrap: wrap;\n      justify-content: center;\n      width: 360px;\n    }\n    #qrDesc{\n      display: block;\n      text-align: center;\n      margin-top: 20px;\n      color: #ffffff;\n      width: 360px;\n    }\n    .codeImg {\n      // display: block;\n      width:256px;\n      height:256px;\n      border-radius: 10px;\n      padding: 10px;\n      border: 2px solid #ffffff;\n    }\n    .codeDesc {\n      display: block;\n      text-align: center;\n      margin-top: 20px;\n      color: #ffffff;\n      width: 360px;\n      font-size: 16px;\n    }\n    .codeDiv {\n      color: #ffffff;\n    }\n    .codeBox {\n      display: flex;\n      text-align: center;\n    }\n    #directions{\n      margin-top: 10px;\n      width: 100%;\n      text-align: left;\n      color: #ffffff;\n      font-size: 8px;\n    }\n    .tech_button {\n      flex:1;\n      height:30px;\n      border-radius: 8px;\n      border: 2px solid var(--border-color);\n      font-size:11px;\n      background:var(--comfy-input-bg);\n      color:var(--error-text);\n      box-shadow:none;\n      cursor:pointer;\n      width: 1rem;\n    }\n    #tech_box {\n      max-height: 80px;\n      display:flex;\n      flex-wrap: wrap;\n      align-items: flex-start;\n    }\n    .uniqueid {\n      display: none;\n    }\n    #showMsgDiv {\n      width:800px;\n      padding: 60px 0;\n      text-align: center;\n      font-size: 30px;\n      color: var(--fg-color);\n    }\n";
(styleElement.innerHTML = cssCode), document.head.appendChild(styleElement);
var techsidkey = "techsid" + window.location.port,
  loading = !1;
const msgBox = $el("div.comfy-modal", { parent: document.body }, []),
  msgDiv = $el("div", { id: "msgDiv" }, "");
msgBox.appendChild(msgDiv),
  (msgBox.style.display = "none"),
  (msgBox.style.zIndex = 10001);
let manager_instance = null;
function setCookie(e, t, i = 1) {
  var s = {
    value: t,
    expires: new Date(new Date().getTime() + 24 * i * 60 * 60 * 1e3),
  };
  localStorage.setItem(e, JSON.stringify(s));
}
function getCookie(e) {
  var t = localStorage.getItem(e);
  return t
    ? ((t = JSON.parse(t)),
      new Date(t.expires) > new Date()
        ? t.value
        : (localStorage.removeItem(e), ""))
    : "";
}
function generateTimestampedRandomString() {
  return (
    Date.now().toString(36) +
    Array(3)
      .fill(0)
      .map(() => Math.random().toString(36).substring(2))
      .join("")
      .substring(0, 18)
  ).substring(0, 32);
}
function showLoading(e = "") {
  hideLoading(),
    (msgDiv.innerText = e || "请稍后..."),
    (msgBox.style.display = "block"),
    (loading = !0);
}
function hideLoading() {
  (msgBox.style.display = "none"), (loading = !1);
}
function showToast(e = "", t = 0) {
  (t = t > 0 ? t : 2e3),
    (msgDiv.innerText = e || "谢谢"),
    (msgBox.style.display = "block"),
    setTimeout(() => {
      msgBox.style.display = "none";
    }, t);
}
var serverUrl = window.location.href;
const qrCode = $el("img", { id: "qrCode", src: "", onerror: () => {} }),
  qrDesc = $el("div", { id: "qrDesc" }, "请用微信扫码，验证身份..."),
  qrBox = $el("div", { id: "qrBox" }, [qrCode, qrDesc]);
app.ui.dialog.element.style.zIndex = 10010;
const showMsgDiv = $el("div", { id: "showMsgDiv" }, "请稍后...");
function showCodeBox(e) {
  app.ui.dialog.close();
  let t = [];
  for (let i = 0; i < e.length; i++)
    t.push(
      $el("div.codeDiv", {}, [
        $el("img.codeImg", { src: e[i].code }),
        $el("div.codeDesc", {}, e[i].desc),
      ])
    );
  const i = $el("div.codeBox", {}, t);
  app.ui.dialog.show(i);
}
function showQrBox(e, t) {
  app.ui.dialog.close(),
    (qrDesc.innerText = t),
    (qrCode.src = e),
    app.ui.dialog.show(qrBox);
}
function hideCodeBox() {
  app.ui.dialog.close();
}
function showMsg(e) {
  app.ui.dialog.close(),
    (showMsgDiv.innerText = e),
    app.ui.dialog.show(showMsgDiv);
}
function hideMsg() {
  app.ui.dialog.close();
}
function tech_alert(e) {
  (loading = !1), showMsg(e);
}

async function requestExe(e, t) {
  var i = localStorage.getItem("comfyuitid") ?? "";
  const s = await api.fetchApi("/manager/tech_zhulu", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ r: e, comfyui_tid: i, postData: t }),
  });
  if (!s.ok)
    return void setTimeout(() => {
      showToast("网络连接出错，请保持电脑联网", 3e3);
    }, 300);
  return await s.json();
}
async function login(e) {
  let t = await requestExe("comfyui.apiv2.code", { s_key: e });
  return "none" != app.ui.dialog.element.style.display
    ? t.data.data.data.techsid.length > 5
      ? t.data.data.data.techsid
      : (await new Promise((e) => setTimeout(e, 800)), await login(e))
    : void 0;
}
async function request(e, t) {
  showLoading("处理中，请稍后...");
  let i = await requestExe(e, t);
  if (41009 != i.errno) return hideLoading(), i;
  {
    let i = await requestExe("comfyui.apiv2.code", { s_key: "" });
    if (i) {
      if (1 == i.data.data.code) {
        hideLoading(), showQrBox(i.data.data.data, i.data.data.desc);
        let s = await login(i.data.data.s_key);
        return (
          hideCodeBox(),
          s
            ? (localStorage.setItem("comfyuitid", s), await request(e, t))
            : void 0
        );
      }
      return void showToast(i.data.data.message);
    }
  }
}
function backWeiget(e) {
  let t = window.appstore_widget ?? {};
  if (e.widgets) {
    let i = { name: e.type, widgets: {} };
    e.widgets.forEach((e, t) => {
      i.widgets[e.name] = {
        type: e.type,
        name: e.name,
        value: e.value,
        options: e.options,
      };
    }),
      (t[e.type] = i);
  }
  window.appstore_widget = t;
}
function chainCallback(e, t, i) {
  if (null != e)
    if (t in e) {
      const s = e[t];
      e[t] = function () {
        const e = s.apply(this, arguments);
        return i.apply(this, arguments), e;
      };
    } else e[t] = i;
  else console.error("Tried to add callback to non-existant object");
}
app.registerExtension({
  name: "ComfyUI_Appstore",
  async beforeRegisterNodeDef(e, t, i) {
    const s = e.prototype.onNodeCreated;
    chainCallback(e.prototype, "onNodeCreated", function () {
      if ((backWeiget(this), "comfyAppstore" === t.name)) {
        const e = s ? s?.apply(this, arguments) : void 0,
          t =
            (this.widgets.findIndex((e) => "zhanwei" === e.name),
            $el("button.tech_button", {
              textContent: "该节点已废弃,请点击屏幕右上角封装应用",
              style: {},
              onclick: async () => {
                hideCodeBox(), tech_alert("请点击屏幕右上角封装应用");
              },
            })),
          i = "1、每创建一个新的“ComfyAppstore”节点，就对应一个新的作品；",
          o = "2、如有问题，联系作者咨询。",
          n = "3、视频教程：",
          d = $el("div", { id: "directions" }, [
            "特殊说明：",
            $el("br"),
            i,
            $el("br"),
            o,
            $el("br"),
            n,
          ]),
          a = $el("div", { id: "tech_box" }, [t, d]);
        this.addDOMWidget("select_styles", "btn", a);
        const c = document.createElement("input");
        return (
          c.setAttribute("type", "text"),
          c.setAttribute("list", "uedynamiclist"),
          c.setAttribute("value", generateTimestampedRandomString()),
          (c.className = "uniqueid"),
          this.addDOMWidget("uniqueid", "input", c, {
            getValue: () => c.value,
            setValue(e) {
              c.value = e;
            },
          }),
          setTimeout(() => {
            this.setSize([420, 500]);
          }, 200),
          e
        );
      }
    }),
      "comfyAppstore" === t.name && (this.serialize_widgets = !0);
  },
}),
  setTimeout(() => {
    (window.comfyui_app = app),
      (window.comfyui_api = api),
      import("/appstore_panel/input.js");
  }, 500),
  app.registerExtension({ name: "Appstore.menu", async setup() {} });
