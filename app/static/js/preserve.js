$(document).ready(function () {
    var today = new Date();
    var month_ago = new Date();
    month_ago.setMonth(today.getMonth() - 1);

    var date_from = $('#date-from-input');
    var date_to = $('#date-to-input');
    var submit = $('#export');

    date_from.val(month_ago.toDateInputValue());
    date_from.change(function () {
        submit.attr('href', "/api/scores/from/" + $(this).val() + "/to/" + date_to.val());
    });

    date_to.val(today.toDateInputValue());
    date_to.change(function () {
        submit.attr('href', "/api/scores/from/" + date_from.val() + "/to/" + $(this).val());
    });

    submit.attr('href', "/api/scores/from/" + date_from.val() + "/to/" + date_to.val());
});

Date.prototype.toDateInputValue = (function () {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0, 10);
});