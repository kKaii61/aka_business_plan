/** @odoo-module **/

import { registry } from "@web/core/registry";
import { GanttController } from "@web_gantt/gantt_controller";
import { GanttView } from "@web_gantt/gantt_view";
import { WorkingShiftRegisterControllerMixin } from "./working_shift_register_controller_mixin";

export class WorkingShiftRegisterGanttController extends GanttController {
    setup() {
//        super.setup();

        // Đăng ký các sự kiện từ mixin
        this.events = {
//            GanttController.prototype.events,
//            WorkingShiftRegisterControllerMixin.events,
        };

        // Tạo một instance của mixin nếu cần
//        this.mixin = new WorkingShiftRegisterControllerMixin();
    }

    async willStart() {
        await super.willStart();
        // Fetch dữ liệu
        this.records = this._fetchRecords();
        this.firstDay = this._fetchFirstDay();
        this.lastDay = this._fetchLastDay();
    }

    _fetchRecords() {
        return this.model.ganttData.records;
    }

    _fetchFirstDay() {
        return this.model.ganttData.startDate;
    }

    _fetchLastDay() {
        return this.model.ganttData.stopDate;
    }

    _displayWarning(warningHtml) {
        const ganttViewEl = this.el.querySelector(".o_gantt_view");
        if (ganttViewEl) {
            ganttViewEl.insertAdjacentHTML("beforebegin", warningHtml);
        }
    }
}

// Tạo Gantt View mới
export const WorkingShiftRegisterGanttView = {
    ...GanttView,
    Controller: WorkingShiftRegisterGanttController,
};

// Đăng ký view mới với registry
registry.category("views").add("working_shift_register_gantt", WorkingShiftRegisterGanttView);






//odoo.define('enmasys_time_off.WorkingShiftRegisterGanttController', function(require) {
//    'use strict';
//
//    var WorkingShiftRegisterControllerMixin = require('enmasys_time_off.WorkingShiftRegisterControllerMixin');
//    var GanttView = require('web_gantt.GanttView');
//    var GanttController = require('web_gantt.GanttController');
//    var viewRegistry = require('web.view_registry');
//
//
//    var WorkingShiftRegisterGanttController = GanttController.extend(WorkingShiftRegisterControllerMixin, {
//        events: _.extend({}, WorkingShiftRegisterControllerMixin.events, GanttController.prototype.events),
//
//        _fetchRecords: function () {
//            return this.model.ganttData.records;
//        },
//        _fetchFirstDay: function () {
//            return this.model.ganttData.startDate;
//        },
//        _fetchLastDay: function () {
//            return this.model.ganttData.stopDate;
//        },
//        _displayWarning: function ($warning) {
//            this.$('.o_gantt_view').before($warning);
//        },
//    });
//
//    var WorkingShiftRegisterGanttView = GanttView.extend({
//        config: _.extend({}, GanttView.prototype.config, {
//            Controller: WorkingShiftRegisterGanttController,
//        }),
//    });
//
//
//    viewRegistry.add('working_shift_register_gantt', WorkingShiftRegisterGanttView);
//
//    return WorkingShiftRegisterGanttController;
//
//});
