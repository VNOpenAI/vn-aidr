"use strict";

$(function () {

    var viewer;

    function showLoading() {
        $(".loading-modal").show();
    }

    function hideLoading() {
        $(".loading-modal").hide();
    }

    function initViewer() {
        if (viewer) {
            viewer.destroy();
        }
        $("#viewer-images").html('<li><img src="' + window.UI["img_placeholder"] + '" alt="Original Image"></li>');
        viewer = new Viewer(document.getElementById('viewer-images'), {
            inline: true,
            navbar: true,
            title: true
        });
        viewer.show();
    }

    $.get("ui-config.json", function (data) {

        window.UI = data;
        var UI = window.UI;

        // Update document attributes
        document.title = data["title"];
        $(".sidebar-brand-text").html(data["sidebar-brand-text"]);
        $(".sidebar-brand-icon img").attr("src", data["logo"]);

        // Load pages
        let section_menu_html = "";
        let sections = data["sections"];

        function updateModelSetting() {
            let currentModelId = $( "#model-selector option:selected" ).val();
            // Update sidebar
            if (window.currentModels[currentModelId]["hide_sidebar"]) {
                $("#prediction-sidebar").hide();
            } else {
                $("#prediction-sidebar").show();
            }
            window.UI.api_endpoint = window.currentModels[currentModelId]["api_endpoint"];
        }
        $("#model-selector").change(function() {
            updateModelSetting();
            initViewer();
        });

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

                    // Models
                    let models = section["models"];
                    window.currentModels = {};
                    let html = "";
                    for (let j = 0; j < models.length; ++j) {
                        html += "<option value='" + models[j].id + "' api_endpoint='" +
                            models[j].api_endpoint + "'>" + models[j].title + "</option>";
                        window.currentModels[models[j]["id"]] = models[j];
                    }
                    $("#model-selector").html(html);
                    updateModelSetting();
                    initViewer();
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

    $("#upload-btn").click(function () {
        $('#upload-file').click();
    });
    $('#upload-file').change(function () {

        showLoading();

        let fd = new FormData();
        let files = $(this)[0].files;
        let filepath = $(this)[0].value;
        let startIndex = (filepath.indexOf('\\') >= 0 ? filepath.lastIndexOf('\\') : filepath.lastIndexOf('/'));
        let filename = filepath.substring(startIndex).replace("\\", "")

        // Check file selected or not
        if (files.length > 0) {
            fd.append('file', files[0]);
            fd.append('filename', filename);
            console.log("Sending request to: " + window.UI.api_endpoint);

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

                    if (!response["prepend_original_image"]) {
                        $("#viewer-images").html("");
                    }

                    for (let i = 0; i < results.length; ++i) {
                        let result = results[i];

                        if ("probability" in result && "label" in result) {
                            let probaValue = (result["probability"] * 100).toFixed(1);      
                            logResult.push(result["label"] + ": " + probaValue + "%");
                            probaTitles.push(result["label"]);
                            probaValues.push(probaValue);
                        }
                        
                        if ("image" in result) {
                            let html = $("#viewer-images").html();
                            $("#viewer-images").html(html + '<li><img src="' + result["image"] + '" alt="' + result["label"] + '"></li>');
                        }
                    }
                    viewer.update();

                    // Update log
                    $("#output-log").val(logResult.join("\n"));

                    // Update chart
                    window.probaChartData.labels = probaTitles;
                    window.probaChartData.datasets[0].data = probaValues;
                    window.probaChart.update();
                    if (probaValues.length > 0) {
                        $("#proba-chart-wrapper").fadeIn();
                    } else {
                        $("#proba-chart-wrapper").fadeOut();
                    }
                    
                    $("#upload-file").val('');
                },
                error: function () {
                    hideLoading();
                    $("#upload-file").val('');
                    initViewer();
                }
            });
            
        } else {
            alert("Please select a file.");
        }
    });

});