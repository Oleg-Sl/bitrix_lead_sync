import BX from './bitrix24/requests.js';                                                                     // модуль выполнения работы к Битрикс
import { createTable as createTableWithRegistredEvents, getRowEventHTML } from "./templates/registered_events_table.js"
import createAppHTML from "./templates/container_app.js"


let events = [
    {
        event: "ONTASKCOMMENTADD",
        handler: "https://app.bits-company.ru/testingevents/events/task-comment-create/",
        offline: 0
    },
    {
        event: "ONTASKCOMMENTUPDATE",
        connector_id: "oneC",
        offline: 1,
    },
    {
        event: "ONUSERADD",
        handler: "https://app.bits-company.ru/testingevents/events/task-comment-create/",
        offline: 0
    }
];

export default class App {
    constructor(container) {
        this.bx = new BX();                     // объект для выполнения запросов к Битрикс через JS библиотеку
        this.container = container;
        this.eventsList = ["wdas", "21", "3d3da2"];
    }

    async init() {
        // this.eventsList = await getEventsList();
        await this.render(events);

        this.elemSelectTypeEvent = this.container.querySelector(".bx24_events__type_event select");
        this.elemSelectNameEvent = this.container.querySelector(".bx24_events__name_event select");
        this.elemInputHandlerEvent = this.container.querySelector(".bx24_events__handler_event input");
        this.elemInputSourceEvent = this.container.querySelector(".bx24_events__source_event input");
        this.btnAddEvent = this.container.querySelector(".bx24_events__add_event button");
        this.setOfflineEvent(this.elemSelectTypeEvent.value)

        this.initHandler();

    }

    initHandler() {
        // Удаление зарегистрированного события
        this.container.addEventListener("click", async (e) => {
            let elemRemoveEvent = e.target.classList.contains("bx24_events__table_events_remove_row_i");
            let elemTr = e.target.closest("tr");
            if (elemRemoveEvent && elemTr) {
                let isRemoveEvent = confirm(`Удалить событие \"${elemTr.dataset.event}\"?`);
                if (!isRemoveEvent) return;
                let parameters = {
                    event: elemTr.dataset.event,
                    event_type: elemTr.dataset.type
                };
                if (elemTr.dataset.type == "online") {
                    parameters.handler = elemTr.dataset.handler;
                }

                console.log("Параметры удаления события: ", parameters);
                let resDel = await this.bx.callMethod("event.unbind", parameters);
                console.log("Результат удаления события: ", resDel);
                if (resDel && resDel.count) {
                    elemTr.remove();
                }
            }
        })

        // Изменение типа события
        this.elemSelectTypeEvent.addEventListener("change", (e) => {
            this.setOfflineEvent(e.target.value);
        })

        // Кнопка содания события
        this.btnAddEvent.addEventListener("click", (e) => {
            this.addEvent();
        })
    }

    async getEventsList() {
        let response = await this.bx.callMethod("events", {});
        return response.result;
    }

    // Регистрирование события
    async addEvent() {
        let isOffline = 0;
        let parameters = {
            event: this.elemSelectNameEvent.value,
            event_type: this.elemSelectTypeEvent.value,
        };
        if (this.elemSelectTypeEvent.value == "online") {
            parameters.handler = this.elemInputHandlerEvent.value;
        } else {
            isOffline = 1
            parameters.auth_connector = this.elemInputSourceEvent.value;
        }
        console.log("Параметры создаваемого события: ", parameters);
        let resAddEvent = await this.bx.callMethod("event.bind", parameters);
        console.log("Результат создания события: ", resDel);
        if (resAddEvent && resAddEvent.result) {
            this.addRecordEventToTable(parameters.event, isOffline, parameters.handler, parameters.auth_connector);
        }
    }

    addRecordEventToTable(eventName, isOffline, eventHandler, eventConnector) {
        this.tBody = this.container.querySelector(".bx24_events__table_events tbody");
        let contentHTML = getRowEventHTML(eventName, isOffline, eventHandler, eventConnector);
        this.tBody.insertAdjacentHTML("beforeend", contentHTML);
    }

    setOfflineEvent(eventType) {
        if (eventType == "offline") {
            this.elemInputHandlerEvent.setAttribute("disabled", "");
            this.elemInputSourceEvent.removeAttribute("disabled");
        } else {
            this.elemInputHandlerEvent.removeAttribute("disabled");
            this.elemInputSourceEvent.setAttribute("disabled", "");
        }
    }

    render(eventsList) {
        let contentRegistredTableHTML = createTableWithRegistredEvents(eventsList);
        let contentHTML = createAppHTML(contentRegistredTableHTML, this.eventsList);
        this.container.innerHTML = contentHTML;
    }

}



document.addEventListener("DOMContentLoaded", () => {
    // BX24.ready(function() {
        console.log('Start');
        let container = document.querySelector("#containerEventsManagement");
        let app = new App(container);
        app.init();
    // })
})
