/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { useBus } from "@web/core/utils/hooks";
import { WebClient } from "@web/webclient/webclient";
import { onWillDestroy, useState } from "@odoo/owl";

patch(WebClient.prototype, {
    setup() {
        super.setup(...arguments);
        this.leftSidebarState = useState({
            collapsedSections: {},
            selectedAppId: null,
        });
        useBus(this.env.bus, "MENUS:APP-CHANGED", () => this.render());
        document.body.classList.add("o_left_sidebar_menu_enabled");
        onWillDestroy(() => {
            document.body.classList.remove("o_left_sidebar_menu_enabled");
        });
    },

    get currentApp() {
        return this.menuService.getCurrentApp() || this.menuService.getMenu(this.leftSidebarState.selectedAppId);
    },

    isLeftSidebarAppActive(app) {
        return this.currentApp?.id === app?.id;
    },

    getLeftSidebarAppSections(app) {
        if (!this.isLeftSidebarAppActive(app)) {
            return [];
        }
        return this.menuService.getMenuAsTree(app.id).childrenTree || [];
    },

    isLeftSidebarSectionCollapsed(section) {
        return Boolean(this.leftSidebarState.collapsedSections[section.id]);
    },

    toggleLeftSidebarSection(section) {
        this.leftSidebarState.collapsedSections[section.id] =
            !this.leftSidebarState.collapsedSections[section.id];
    },

    async onLeftSidebarHomeClick() {
        if (this.hm) {
            return this.hm.toggle(true);
        }
        return this._loadDefaultApp();
    },

    async onLeftSidebarAppSelection(app) {
        if (!app) {
            return;
        }
        if (this.hm?.hasHomeMenu) {
            this.hm.toggle(false);
        }
        this.leftSidebarState.selectedAppId = app.id;
        this.render();
        if (app.actionID) {
            await this.menuService.selectMenu(app);
        } else {
            this.menuService.setCurrentMenu(app);
        }
        this.leftSidebarState.selectedAppId = this.menuService.getCurrentApp()?.id || app.id;
    },

    async onLeftSidebarMenuSelection(menu) {
        if (!menu) {
            return;
        }
        if (this.hm?.hasHomeMenu) {
            this.hm.toggle(false);
        }
        this.leftSidebarState.selectedAppId = menu.appID || this.leftSidebarState.selectedAppId;
        await this.menuService.selectMenu(menu);
    },

    getLeftSidebarMenuItemHref(payload) {
        return `/odoo/${payload.actionPath || "action-" + payload.actionID}`;
    },
});
