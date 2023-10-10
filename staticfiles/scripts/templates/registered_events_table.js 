function getRowEventHTML(name, isOffline, handler, connectorId) {
    let typeEventRus = isOffline ? "оффлайн" : "онлайн";
    let typeEventEng = isOffline ? "offline" : "online";
    return `
        <tr data-event="${name}" data-handler="${handler}" data-type="${typeEventEng}" data-connector="${connectorId}">
            <td scope="row">${name}</td>
            <td>${typeEventRus}</th>
            <td>${handler || ""}</td>
            <td>${connectorId || ""}</td>
            <td>
                <div class="table-cell-settings bx24_events__table_events_remove_row">
                    <i class="bi bi-trash bx24_events__table_events_remove_row_i" title="Удалить"></i>
                </div>
            </td>
        </tr>
    `;
}

function generateTbodyHTML(eventsData) {
    let content = '';
    for (let eventData of eventsData) {
        content += getRowEventHTML(eventData.event, eventData.offline, eventData.handler, eventData.connector_id);
    }
    return content
}


function createTable(eventsData) {
    let content = `
        <table class="table table-hover table-bordered caption-top bx24_events__table_events">
            <caption>Список установленных обработчиков событий</caption>
            <thead>
                <tr>
                    <th scope="col">Событие</th>
                    <th scope="col">Тип события</th>
                    <th scope="col">URL обработчика</th>
                    <th scope="col">Коннектор</th>
                    <th scope="col"></th>
                </tr>
            </thead>
            <tbody>
                ${generateTbodyHTML(eventsData)}
            </tbody>
        </table>
    `;
    return content;
}

export {createTable, getRowEventHTML}
