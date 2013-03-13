

function basic_datatable_options(header_id, save_name, wrapper_id, message_id) {
	var options = {
		"sPaginationType": "bootstrap",
		"fnInitComplete": function() {
			this.fnAdjustColumnSizing(true);
			var num_rows = this.fnSettings().fnRecordsTotal();
			document.getElementById(header_id).innerHTML = '(' + num_rows + ')';
			if(num_rows == 0) {
    			 document.getElementById(message_id).style.display = 'block';
    			 document.getElementById(wrapper_id).style.display = 'none';
			}
		},	
		"sDom": '<"clear">lfrtipT',
        "oTableTools": {
        	"aButtons": [
				"copy",
				"print",
				{
					"sExtends": "csv",
					"sTitle": save_name + '.csv'
				},
				{
					"sExtends": "xls",
					"sTitle": save_name + '.xls'
				}	
			],
        	"sSwfPath": "../static/js/copy_csv_xls_pdf.swf"
		}
	};
	return options;
  	 
}

function setup_cytoscape_vis(graph_link) {
		// id of Cytoscape Web container div
		var div_id = "cytoscapeweb";
                                
		// visual style we will use
		var visual_style = {
			nodes: {
				color: {
					discreteMapper: {
						attrName: "focus",
						entries: [
							{ attrValue: '1', value: "#fade71" }
						]
					}
				},
				labelHorizontalAnchor: "center"
			},
		};
                
		// initialization options
		var options = {
		swfPath: "../static/js/CytoscapeWeb",
		flashInstallerPath: "/swf/playerProductInstall"
	};
                
	// init and draw
	var vis = new org.cytoscapeweb.Visualization(div_id, options);
	
	var evidence_cutoff = 3;
	
	// callback when Cytoscape Web has finished drawing
    vis.ready(function() {
                
		// add a listener for when nodes and edges are clicked
		vis.addListener("click", "nodes", function(event) {
			handle_click(event);
		})
		.addListener("click", "edges", function(event) {
			handle_click(event);
		});
                    
		function handle_click(event) {
			var target = event.target;   
			var link = target.data['link']
			window.location.href = link          
		}
		var max_evidence = Math.min(10, vis.nodes()[vis.nodes().length-1].data.evidence);
		$(function() {
			$( "#slider-range-min" ).slider({
				range: "max",
				value: 3,
				min: evidence_cutoff,
				max: max_evidence,
				step: 1,
				slide: function( event, ui ) {
					handle_slide(event, ui);
				},
				change: function( event, ui ) {
					handle_slide(event, ui);
				}
			});
			function handle_slide(event, ui) {
				var val = $( "#amount" ).val( "$" + ui.value );
				vis.filter(function(item) {
					return item.data.evidence == -1 || item.data.evidence >= ui.value;
				});
				vis.layout('ForceDirected');
			}
			$( "#slider-range-min" ).slider('value', 3);
			
			var $slider =  $('#slider-range-min');
			var max =  $slider.slider("option", "max") - $slider.slider("option", "min") + 1;    
 			var spacing =  100 / (max -1);
 			var multiplier = 1;
 			if (max > 25) {
 				multiplier = 2;
 			}

    		$slider.find('.ui-slider-tick-mark').remove();
    		for (var i = 0; i < max ; i=i+multiplier) {
    			var value = (i+evidence_cutoff);
    			if(value >= 10) {
    				var left = ((spacing * i)-1)
        			$('<span class="ui-slider-tick-mark muted">10+</span>').css('left', left + '%').appendTo($slider);
    			}
    			else {
    				var left = ((spacing * i)-.5)
					$('<span class="ui-slider-tick-mark muted">' +value+ '</span>').css('left', left + '%').appendTo($slider);
    			}
        	}
		});
	});
		//Grab the network data via AJAX
	$.get(graph_link, function(data) {
		vis.draw({ network: data, visualStyle: visual_style});
		evidence_cutoff = data['evidence_cutoff']
	});          
}
