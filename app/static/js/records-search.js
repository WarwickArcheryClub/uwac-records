function clamp(elem, max) {
    if (max <= elem.val()) {
        elem.val(max);
    }
}

Date.prototype.toDateInputValue = (function () {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0, 10);
});

$(document).ready(function () {
    $("#date-input").val(new Date().toDateInputValue());
    $(".select2").select2({
        ajax: {
            cache: true,
            headers: {
                "X-CSRFToken": csrftoken
            },
            data: function (params) {
                return {
                    "query": params.term
                };
            },
            type: "POST",
            dataType: "json"
        },
        minimumInputLength: 3
    });
    $("#round-select").on("select2:select", function(event) {
        var round = event.params.data;

        clamp($("#score-hits").attr({
            "max": round.max_hits
        }), round.max_hits);
        clamp($("#score-golds").attr({
            "max": round.max_hits
        }), round.max_hits);
        clamp($("#score-score").attr({
            "max": round.max_score
        }), round.max_score);
        if (round.type === "Indoors" || round.type === "Imperial" || round.type === "Clout") {
            $("#score-xs").prop("disabled", true);
        } else {
            $("#score-xs").prop("disabled", false);
        }
    });
    $("#search-data").val("");
    $("#search-input").devbridgeAutocomplete({
        serviceUrl: '/api/suggestions',
        onSelect: function (x) {
            $(this).val(x.value);
            $("#search-data").val(JSON.stringify(x));
        },
        zIndex: 94,
        ajaxSettings: {
            "headers": {
                "X-CSRFToken": csrftoken
            }
        },
        dataType: "json",
        type: "POST"
    });
    var $browse = $("#browse");
    var $submit = $("#submit");
    var $tabs = $(".form-tab a");
    $tabs.click(function (event) {
        event.preventDefault();
        var $tab = $(event.currentTarget).attr("href");
        if ($tab === "#submit") {
            $browse.removeClass("content-active");
            $submit.addClass("content-active");
            $("#submit-tab").addClass("active");
            $("#browse-tab").removeClass("active");
        } else if ($tab === "#browse") {
            $submit.removeClass("content-active");
            $browse.addClass("content-active");
            $("#submit-tab").removeClass("active");
            $("#browse-tab").addClass("active");
        }
    });
});
