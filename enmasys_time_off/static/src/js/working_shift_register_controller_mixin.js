/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { onWillUpdateProps } from "@odoo/owl";

export class WorkingShiftRegisterControllerMixin extends Component {
    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.time = useService("time");

        this.firstDay = null;
        this.lastDay = null;

        // Tải ngày đầu tiên và ngày cuối cùng
        this.loadDates();

        // Đăng ký sự kiện cập nhật props
        onWillUpdateProps(() => {
            this._renderWorkingShiftRegisterButtons();
        });
    }

    async loadDates() {
        this.firstDay = (await this._fetchFirstDay()).toDate();
        this.lastDay = (await this._fetchLastDay()).toDate();
    }

    _renderWorkingShiftRegisterButtons() {
        if (this.props.modelName !== "working.shift.register") return;

        const buttonHtml = `
            <button class="btn btn-primary btn-copied-last-week">
                ${this.env._t("Sao chép tuần trước")}
            </button>`;

        // Cập nhật HTML
        this.el.innerHTML = buttonHtml;

        // Thêm sự kiện cho nút
        this.el.querySelector('.btn-copied-last-week').addEventListener('click', (e) => this._onCopiedLastWeek(e));
    }

    async _copiedLastWeek() {
        await this.orm.call("working.shift.register", "copy_last_week", [
            [],
            this.time.date_to_str(this.firstDay),
            this.time.date_to_str(this.lastDay),
        ]);
        this.action.reload();
    }

    _onCopiedLastWeek(event) {
        event.preventDefault();
        this._copiedLastWeek();
    }

    async _fetchFirstDay() {
        return moment().startOf('isoWeek');
    }

    async _fetchLastDay() {
        return moment().endOf('isoWeek');
    }
}








odoo.define('enmasys_time_off.WorkingShiftRegisterControllerMixin', function(require) {
    'use strict';

    var core = require('web.core');
    var time = require('web.time');

    var _t = core._t;
    var QWeb = core.qweb;

    /*
        This mixin implements the behaviours necessary to generate and validate work entries and Payslips
        It is intended to be used in a Controller and requires four methods to be defined on your Controller

         1. _fetchRecords
            Which should return a list of records containing at least the state and id fields

         2. _fetchFirstDay
            Which should return the first day for which we will generate the work entries, it should be a Moment instance
            (Typically the first day of the current month)

         3. _fetchLastDay
            Same as _fetchFirstDay except that this is the last day of the period

         4. _displayWarning
            Which should insert in the DOM the warning rendered template received as argument.

        This mixin is responsible for rendering the buttons in the control panel and adds the two following methods

        1. _generateWorkEntries
    */

    var WorkingShiftRegisterControllerMixin = {

        /**
         * @override
         * @returns {Promise}
         */
        _update: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._renderWorkingShiftRegisterButtons();
                self.firstDay = self._fetchFirstDay().toDate();
                self.lastDay = self._fetchLastDay().toDate();
                var now = moment();
                if (self.firstDay > now) return Promise.resolve();
            });
        },

        _renderWorkingShiftRegisterButtons: function () {
            if (this.modelName !== "working.shift.register") {
                return;
            }

            var records = this._fetchRecords();

            this.$buttons.find('.btn-work-entry').remove();

            this.$buttons.append(QWeb.render('hr_work_entry.work_entry_button', {
                button_text: _t("Sao chép tuần trước"),
                event_class: 'btn-copied-last-week',
            }));
            this.$buttons.find('.btn-copied-last-week').on('click', this._onCopiedLastWeek.bind(this));

        },

        _copiedLastWeek: function () {
            var self = this;
            return this._rpc({
                model: 'working.shift.register',
                method: 'copy_last_week',
                args: [[], time.date_to_str(this.firstDay), time.date_to_str(this.lastDay)],

            }).then(function () {
                self.reload();
            })
        },

        _onCopiedLastWeek: function (e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            this._copiedLastWeek();
        },

    };

    return WorkingShiftRegisterControllerMixin;

});
