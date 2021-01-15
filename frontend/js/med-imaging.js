$(function () {

    'use strict';

    var viewer;

    function showLoading() {
        $(".loading-modal").show();
    }

    function hideLoading() {
        $(".loading-modal").hide();
    }

    $.get("ui-config.json", function (data) {

        window.UI = {};
        var UI = window.UI;

        // Update document attributes
        document.title = data["title"];
        $(".sidebar-brand-text").html(data["sidebar-brand-text"]);
        $(".sidebar-brand-icon img").attr("src", data["logo"]);

        // Load pages
        let section_menu_html = "";
        let sections = data["sections"];
        UI.sections = sections;

        function selectFeature(section_id) {
            $("#proba-chart-wrapper").hide();
            $("#section-menu li").removeClass("active");
            for (let i = 0; i < window.UI.sections.length; ++i) {
                let section = window.UI.sections[i];
                if (section["id"] == section_id) {
                    console.log("Select: " + section_id);
                    $('#section-title').html(section["title"]);
                    $('#section-menu li[name="' + section_id + '"]').addClass("active");
                    $("#output-log").val('');
                    window.UI.api_endpoint = section["api_endpoint"];
                    $("#viewer-images").html('<img src="' + section["img_placeholder"] + '" alt="VN AIDr">');
                    viewer.update();
                    viewer.moveTo(0, 0);
                    break;
                }
            }
        }

        // Draw menu
        for (let i = 0; i < sections.length; ++i) {
            section_menu_html += '<li name="' + sections[i]["id"] + '" class="nav-item">' +
                '<a class="nav-link" href="#">' +
                '<i class="fas ' + sections[i]["icon"] + '"></i>' +
                '<span>' + sections[i]["title"] + '</span></a></li>';
        }
        $("#section-menu").html(section_menu_html);
        $("#section-menu li").each(function () {
            $(this).click(function () {
                selectFeature($(this).attr("name"));
            });
        });
        $("#section-menu li").first().click();


    });

    // View an image
    viewer = new Viewer(document.getElementById('viewer-images'), {
        inline: true,
        navbar: true,
        title: true
    });
    viewer.show();

    $("#upload-btn").click(function () {
        $('#upload-file').click();
    });
    $('#upload-file').change(function () {

        showLoading();

        let fd = new FormData();
        let files = $(this)[0].files;

        // Check file selected or not
        if (files.length > 0) {
            fd.append('file', files[0]);
            console.log("Sending request to: " + window.UI.api_endpoint);

            // Show original image
            let reader = new FileReader();
            reader.onload = (function() {
                return function(e) {
                    $("#viewer-images").html('<li><img src="' + e.target.result + '" alt="Original Image"></li>');
                };
            })();
            reader.readAsDataURL(files[0]);

            $.ajax({
                url: window.UI.api_endpoint,
                type: 'post',
                data: fd,
                contentType: false,
                processData: false,
                success: function (response) {

                    hideLoading();
                    let results = response["results"];
                    let logResult = [];
                    let probaTitles = [];
                    let probaValues = [];
                    for (let i = 0; i < results.length; ++i) {
                        let result = results[i];
                        let probaValue = (result["probability"] * 100).toFixed(1);      
                        logResult.push(result["label"] + ": " + probaValue + "%");
                        probaTitles.push(result["label"]);
                        probaValues.push(probaValue);
                        if ("image" in result) {
                            let html = $("#viewer-images").html();
                            $("#viewer-images").html(html + '<li><img src="' + result["image"] + '" alt="' + result["label"] + '"></li>');
                        }
                    }
                    viewer.update();
                    viewer.moveTo(0, 0);

                    // Update log
                    $("#output-log").val(logResult.join("\n"));

                    // Update chart
                    $("#proba-chart-wrapper").fadeIn();
                    window.probaChartData.labels = probaTitles;
                    window.probaChartData.datasets[0].data = probaValues;
                    window.probaChart.update();
                },
                error: function () {
                    hideLoading();
                }
            });
            $(this).val('');
        } else {
            alert("Please select a file.");
        }
    });

});