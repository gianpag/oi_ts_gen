/*  Adjust some parameters to make the metric generation more responsive... 
*   1. Adjust the frequency of MID server process metric data 
*   2. adjust the eviction size
*/

(function() {
	var grext = new GlideRecord("ecc_agent_ext");
	if (!grext.get("name", "ITOA MetricExtension"))
		return;
	
	//This adjusts how often the MID server processes the metric data
	var gr = new GlideRecord("ecc_agent_ext_context_metric");
	gr.addQuery("extension", grext.sys_id);
	gr.query();
	while (gr.next()) {
		gr.batcher_max_delay_time = 10000;
		gr.batcher_metric_max_lag_time = 10000;
		gr.update();
	}
	
}());

(function() {
	var maxValue = 144000;
	var evictionSysIds = [];
	
	var gr = new GlideRecord("sa_metric_config_setting");
	gr.addQuery("name", "CONTAINS", "eviction_size");
	gr.query();
	while (gr.next()) {
		gr.max = maxValue;
		gr.update();
		evictionSysIds.push(gr.sys_id+'');
	}
	
	var ruleName = "Eviction Size";
	var gr = new GlideRecord("sa_metric_config_rule");
	if (gr.get("name", ruleName))
		return;
	
	gr.initialize();
	gr.name = ruleName;
	var mcrSysId = gr.insert();
	
	for (var i=0; i<evictionSysIds.length; i++) {
		var grr = new GlideRecord("sa_metric_config_rule_setting");
		grr.rule = mcrSysId;
		grr.name = evictionSysIds[i];
		grr.value = maxValue;
		
		grr.insert();
	}	
	
	var rec = new GlideRecord('sysauto_script');
	rec.get('name', 'Operational Metrics - Metric configuration job');
	SncTriggerSynchronizer.executeNow(rec);	
	
}());

