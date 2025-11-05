/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

export class YouthImportTemplateButton extends Component {
    static template = "youth_tracking.ImportTemplateButton";
    
    downloadTemplate() {
        window.location.href = "/youth/download_import_template";
    }
}

registry.category("actions").add("youth_download_template", YouthImportTemplateButton);
