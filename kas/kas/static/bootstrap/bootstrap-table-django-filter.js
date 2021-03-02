function paginationParams(params) {
    "use strict";
    if (params.sortOrder === 'desc') {
        params.ordering = '-' + params.sortName;
    } else {
        params.ordering = params.sortName;
    }
    if (params.searchText ==='') {
        delete params.searchText;
    }
    delete params.sortName;
    delete params.sortOrder;
    params.limit = 10
    return params;
}

function queryParams(params){
    "use strict";
    let pagedParams = paginationParams(params);
    //get the bootstrap tables
    document.querySelectorAll('[data-toggle=table]').forEach(table =>{
        $(table.dataset.toolbar).find('select, input').each(function(index, elem){
            if ($(this).val() !=='null'){
                pagedParams[$(this).attr('name')] = $(this).val();
            }
        });
    });
    return pagedParams;
}
