$(document).ready(function () {
    $("#date-input").val(scoreDate);
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
        minimumInputLength: 2
    });
    $("#round-select").on("select2:select", function (event) {
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
        if (round.type.indexOf("Indoors") > -1 || round.type === "Imperial" || round.type === "Clout") {
            $("#score-xs").prop("disabled", true);
        } else {
            $("#score-xs").prop("disabled", false);
        }
    });
});
