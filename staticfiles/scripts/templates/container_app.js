function getOptionsHTML(eventsList) {
    let contentHTML = '';
    for (let event of eventsList) {
        contentHTML += `<option value="${event}">${event}</option>`;
    }
    return contentHTML;
}


export default function createAppHTML(contentRegistredTableHTML, eventsList) {
    let content = `
        <div class="bx24_events__table_events_container">
            ${contentRegistredTableHTML}
        </div>

        <div class="bx24_events__registry_event_container">
            <h4>Регистрация событий</h4>
            <div class="border border-1 rounded p-3">
                <div class="bx24_events__type_event">
                    <label for="registry_event__selectTypeEvent" class="form-label">Тип события</label>
                    <select class="form-select bx24_events__registry_event_select" aria-label="Default select example" id="registry_event__selectTypeEvent">
                        <option value="online" selected>Онлайн</option>
                        <option value="offline">Оффлайн</option>
                    </select>
                </div>
                <div class="bx24_events__name_event">
                    <label for="name_event__selectTypeEvent" class="form-label">Название события</label>
                    <select class="form-select" aria-label="Default select example" id="name_event__selectTypeEvent">
                        ${getOptionsHTML(eventsList)}
                    </select>
                </div>
                <div class="bx24_events__handler_event">
                    <label for="name_event__handlerEvent" class="form-label">URL обработчика</label>
                    <input class="form-control" type="text" placeholder="..." aria-label="input example" id="name_event__handlerEvent">
                </div>
                <div class="bx24_events__source_event">
                    <label for="name_event__sourceKey" class="form-label">Ключ источника</label>
                    <input class="form-control" type="text" placeholder="..." aria-label="input example" id="name_event__sourceKey">
                </div>
                <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-2 bx24_events__add_event">
                    <button class="btn btn-primary me-md-2" type="button">Добавить</button>
                </div>
            </div>
        </div>
    `;
    return content;
}
