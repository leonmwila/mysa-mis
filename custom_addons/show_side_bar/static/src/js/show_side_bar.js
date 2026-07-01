/** @odoo-module **/

const ROOT_CLASS = "o_show_side_bar_enabled";
const PANEL_ID = "o_show_side_bar_panel";
const LIST_ID = "o_show_side_bar_list";
let bootstrapDone = false;

function onBackendPage() {
    return window.location.pathname.startsWith("/odoo") || window.location.pathname.startsWith("/web");
}

function getAppsToggle() {
    return document.querySelector(".o_navbar_apps_menu .dropdown-toggle, .o_navbar_apps_menu button");
}

function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) {
        return panel;
    }

    panel = document.createElement("aside");
    panel.id = PANEL_ID;
    panel.innerHTML = `
        <div class="o_show_side_bar_header">Menu</div>
        <nav class="o_show_side_bar_nav">
            <ul id="${LIST_ID}" class="o_show_side_bar_list"></ul>
        </nav>
    `;
    document.body.appendChild(panel);
    return panel;
}

function extractAppItems() {
    return Array.from(document.querySelectorAll(".dropdown-menu .o_app[data-menu-xmlid]"))
        .map((el) => ({
            name: (el.textContent || "").trim(),
            href: el.getAttribute("href") || "/odoo",
        }))
        .filter((item) => item.name);
}

function renderItems(items) {
    const list = document.getElementById(LIST_ID);
    if (!list) {
        return;
    }

    if (!items.length) {
        list.innerHTML = '<li class="o_show_side_bar_empty">No menu items yet</li>';
        return;
    }

    const currentPath = window.location.pathname;
    list.innerHTML = items
        .map((item) => {
            const isActive = currentPath === item.href || currentPath.startsWith(item.href + "/");
            return `<li><a class="o_show_side_bar_link${isActive ? " is-active" : ""}" href="${item.href}">${item.name}</a></li>`;
        })
        .join("");
}

function refreshSidebar() {
    if (!onBackendPage()) {
        return;
    }

    document.body.classList.add(ROOT_CLASS);
    ensurePanel();

    const toggle = getAppsToggle();
    if (!toggle) {
        renderItems([]);
        return;
    }

    // Open once so Odoo renders app entries in the dropdown menu (rendered in portal).
    if (toggle.getAttribute("aria-expanded") !== "true") {
        toggle.click();
    }

    window.setTimeout(() => {
        const items = extractAppItems();
        renderItems(items);
    }, 120);
}

function bootstrapSidebarBehavior() {
    if (bootstrapDone) {
        return;
    }
    bootstrapDone = true;

    refreshSidebar();
    window.addEventListener("hashchange", () => {
        window.setTimeout(refreshSidebar, 120);
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootstrapSidebarBehavior, { once: true });
} else {
    bootstrapSidebarBehavior();
}
