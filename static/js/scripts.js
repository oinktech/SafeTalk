document.addEventListener('contextmenu', function (e) {
    e.preventDefault();
});

document.addEventListener('keydown', function (e) {
    if (e.ctrlKey && (e.key === 's' || e.key === 'c' || e.key === 'v' || e.key === 'a')) {
        e.preventDefault();  // 禁用 Ctrl + S, Ctrl + C, Ctrl + V, Ctrl + A
    }
});

// 禁止选取文本
document.addEventListener('selectstart', function (e) {
    e.preventDefault();
});

// 禁止截屏（限制屏幕录制和截图的有效性）
window.addEventListener("keydown", function(event) {
    if (event.key === "PrintScreen") {
        event.preventDefault();
        alert("截屏已禁用。");
    }
});
