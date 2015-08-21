$(document).ready(function () {
    $.tablesorter.addParser({
        id: 'scores',
        is: function (s) {
            return false
        },
        format: function (s) {
            return parseInt(s.replace(/\/[0-9]*/g, ''));
        },
        type: 'numeric'
    });
    var sort_opts = {
        cssAsc: 'sort-ascending',
        cssDesc: 'sort-descending',
        cssHeader: 'sort-header',
        headers: {}
    };
    sort_opts.headers[class_column] = {sorter: false};
    $('.sortable').tablesorter(sort_opts);
});
