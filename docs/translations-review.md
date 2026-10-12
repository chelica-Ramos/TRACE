# TRACE translation review

Every app-owned string in the EN/TL dictionaries is listed below.
Technical terms and proper names intentionally remain in English where natural.

| Key | English | Tagalog |
| --- | --- | --- |
| `tracey_offline_missing_model` | llama3 is not installed. Offline mode cannot download it. Connect to the internet and run `ollama pull llama3` once, then restart TRACE offline. | Hindi pa naka-install ang llama3. Hindi ito mada-download sa offline mode. Kumonekta sa internet at patakbuhin ang `ollama pull llama3` nang isang beses, tapos i-restart ang TRACE offline. |
| `page_title` | TRACE \| Budget Intelligence | TRACE \| Gabay sa Budget |
| `language_label` | Language | Wika |
| `language_en` | English | English |
| `language_tl` | Tagalog | Tagalog |
| `preparing` | Preparing budget intelligence… | Inihahanda ang budget insights… |
| `training` | Training progress model… | Tina-train ang progress model… |
| `missing_columns` | Missing columns: {columns} | May kulang na columns: {columns} |
| `unavailable` | Unavailable | Walang available na data |
| `tracey_title` | 💬 Tracey | 💬 Tracey |
| `tracey_greeting` | Big eyes, hard hat, bottomless curiosity. Ask me where the pesos went. | Malaki ang mata, naka-hard hat, at uhaw sa sagot. Tanungin mo ako kung saan napunta ang mga piso. |
| `tracey_local` | Local conversations powered by Ollama. The first model download requires internet. | Lokal ang chat gamit ang Ollama. Kailangan ng internet sa unang pag-download ng model. |
| `tracey_missing_package` | Tracey needs the Ollama Python library. Install the project dependencies with `python -m pip install -r requirements.txt`, then restart Streamlit. | Kailangan ni Tracey ang Ollama Python library. I-install ang project dependencies gamit ang `python -m pip install -r requirements.txt`, tapos i-restart ang Streamlit. |
| `tracey_missing_path` | Ollama was not found on PATH. Restart your terminal or IDE after installing Ollama. | Hindi makita ang Ollama sa PATH. I-restart ang terminal o IDE pagkatapos i-install ang Ollama. |
| `tracey_downloading` | Tracey is downloading her language model... Please wait, this may take a few minutes if it's the first time. | Dina-download ni Tracey ang language model niya... Sandali lang, puwedeng abutin ng ilang minuto sa unang download. |
| `tracey_download_error` | Unable to download llama3. Check your internet connection and Ollama server. | Hindi ma-download ang llama3. Tingnan ang internet connection at Ollama server mo. |
| `tracey_placeholder` | Ask Tracey about budgets, utilization, or data analysis… | Tanungin si Tracey tungkol sa budget, utilization, o data analysis… |
| `tracey_thinking` | Tracey is thinking… | Nag-iisip si Tracey… |
| `tracey_empty_response` | Ollama returned an empty response. Please try again. | Walang sagot na ibinalik ang Ollama. Subukan ulit. |
| `tracey_connection_error` | Tracey cannot connect to Ollama. Start the Ollama application or run `ollama serve`, then try again. | Hindi makakonekta si Tracey sa Ollama. Buksan ang Ollama app o patakbuhin ang `ollama serve`, tapos subukan ulit. |
| `tracey_ollama_error` | Ollama error: {error} | May error sa Ollama: {error} |
| `tracey_request_error` | Tracey could not complete this request: {error} | Hindi natapos ni Tracey ang request na ito: {error} |
| `tracey_loading` | Hard hat on — preparing the project data. | Naka-hard hat na — inihahanda ang project data. |
| `tracey_find_projects` | Let’s find some projects together! | Hanap tayo ng mga project! |
| `tracey_budget_empty` | Ready to inspect when budget data is available. | Ready nang mag-inspect kapag may budget data na. |
| `tracey_search_empty` | Try another keyword — I’m ready to help! | Subukan ang ibang keyword — ready akong tumulong! |
| `tracey_descriptions_empty` | No unfinished descriptions to inspect today. | Walang description ng unfinished projects na puwedeng suriin ngayon. |
| `tracey_accessible` | Tracey the tarsier construction worker | Si Tracey, ang tarsier na construction worker |
| `tracey_happy_label` | Make Tracey happy | Pasayahin si Tracey |
| `tracey_mascot` | Tracey mascot | Mascot na si Tracey |
| `chip_project` | What is TRACE? | Ano ang TRACE? |
| `chip_data` | What data do we use? | Anong data ang gamit natin? |
| `chip_flags` | How do we flag items? | Paano natin fina-flag ang mga item? |
| `chip_limits` | What are the limits? | Ano ang mga limitasyon? |
| `chip_tfidf` | Explain TF-IDF | Ipaliwanag ang TF-IDF |
| `dataset_error` | Unable to load dataset: {error} | Hindi ma-load ang dataset: {error} |
| `sidebar_caption` | PUBLIC FINANCE INTELLIGENCE | MGA INSIGHT SA PAMPUBLIKONG PONDO |
| `region` | Region | Region |
| `year` | Year | Taon |
| `filter_note` | Empty selections include all values. Dashboard charts and the regression model follow these filters. | Kapag walang pinili, kasama lahat ng values. Sinusunod ng dashboard charts at regression model ang mga filter na ito. |
| `scope_projects` | Projects in scope | Mga project sa napiling saklaw |
| `hero_eyebrow` | ALLOCATION • UTILIZATION • ACCOUNTABILITY | ALLOCATION • UTILIZATION • PANANAGUTAN |
| `project_full_name` | Taxpayer Resource Allocation & Expenditure Oversight | Taxpayer Resource Allocation & Expenditure Oversight |
| `hero_tagline` | A clearer view of public infrastructure funding. | Mas malinaw na pagtingin sa pondo para sa pampublikong imprastraktura. |
| `methodology` | Utilization is estimated as Budget × Progress / 100, assuming spending proportional to physical completion. Actual payments are unavailable. | Tinatantya ang utilization bilang Budget × Progress / 100, sa palagay na proporsyonal ang gastos sa aktuwal na pagkakumpleto ng project. Walang available na data ng aktuwal na bayad. |
| `no_filter_matches` | No projects match your filters. Adjust Region or Year. | Walang project na tugma sa filters mo. Baguhin ang Region o Taon. |
| `tab_overview` | Executive Dashboard | Executive Dashboard |
| `tab_explorer` | Project Explorer | Hanap ng Project |
| `tab_insights` | AI Insights | AI Insights |
| `tab_tracey` | Tracey | Tracey |
| `total_projects` | Total Projects | Kabuuang Bilang ng Project |
| `scope_records` | Records in the current scope | Mga record sa kasalukuyang saklaw |
| `total_allocated` | Total Allocated Budget | Kabuuang Inilaang Budget |
| `total_utilized` | Total Utilized Budget | Kabuuang Nagamit na Budget |
| `estimated_prefix` | Estimated ·  | Tantiya ·  |
| `average_progress` | Average Progress | Average na Progress |
| `unweighted_average` | Unweighted project average | Average ng mga project na pantay-pantay ang bigat |
| `portfolio_status` | Portfolio status | Status ng mga project |
| `regional_comparison` | Regional allocation & utilization | Allocation at utilization bawat region |
| `no_budget_pairs` | No valid budget-utilization pairs. | Walang valid na pares ng budget at utilization. |
| `allocated` | Allocated | Inilaan |
| `estimated_utilized` | Estimated utilized | Tantiyang nagamit |
| `budget_php` | Budget (PHP) | Budget (PHP) |
| `funding_gaps` | Unfinished projects with the largest estimated funding gaps | Mga unfinished project na may pinakamalaking tantiyang natitirang budget |
| `ongoing_note` | On-Going means unfinished; a delay requires planned deadlines and a reporting date. | Ang On-Going ay hindi pa tapos; kailangan ng nakaplanong deadline at reporting date para masabing delayed. |
| `explore_title` | Explore the project portfolio | Tingnan ang mga project |
| `search_label` | Search Contract ID or Description | Maghanap gamit ang Contract ID o Description |
| `search_placeholder` | Enter a contract ID, road, bridge, or other keyword | Maglagay ng contract ID, kalsada, tulay, o ibang keyword |
| `matching_records` | {count:,} matching records | {count:,} record ang tugma |
| `no_search_matches` | No matching projects in this scope. | Walang tugmang project sa saklaw na ito. |
| `select_project` | Select a project to inspect | Pumili ng project na titingnan |
| `choose_project` | Choose a project | Pumili ng project |
| `record_number` | record {number} | record {number} |
| `contract_title` | Contract {contract} | Contract {contract} |
| `contractor_label` | Contractor: | Contractor: |
| `location_label` | Location: | Lokasyon: |
| `status` | Status | Status |
| `not_recorded` | Not recorded | Walang record |
| `start_date_label` | Start date: | Petsa ng pagsisimula: |
| `completion_date_label` | Completion date: | Petsa ng pagkakumpleto: |
| `physical_progress` | Physical progress: {progress:.2f}% | Aktuwal na progress: {progress:.2f}% |
| `invalid_progress` | Progress is not recorded or is invalid. | Walang record ng progress o hindi valid ang value nito. |
| `themes_title` | Themes in unfinished projects | Mga tema sa unfinished projects |
| `tfidf_note` | TF-IDF surfaces descriptive themes, not proof of anomalies or reasons for delays. | Ipinapakita ng TF-IDF ang mga tema sa descriptions, hindi patunay ng anomalya o dahilan ng delay. |
| `no_ongoing_descriptions` | No On-Going descriptions in this scope. | Walang description ng On-Going projects sa saklaw na ito. |
| `tfidf_count` | Computed from {count:,} On-Going project descriptions. | Kinalkula mula sa {count:,} description ng On-Going projects. |
| `no_terms` | No usable terms after preprocessing. | Walang magagamit na salita pagkatapos ng preprocessing. |
| `prediction_title` | Progress prediction | Prediction ng progress |
| `prediction_note` | Linear regression estimates physical progress from Budget alone, using the filtered records. | Tinatantya ng linear regression ang aktuwal na progress gamit lang ang Budget mula sa na-filter na records. |
| `prediction_minimum` | At least five valid records are needed. Broaden your filters. | Kailangan ng hindi bababa sa limang valid na record. Palawakin ang filters mo. |
| `hypothetical_budget` | Hypothetical Budget (PHP) | Halimbawang Budget (PHP) |
| `estimate_progress` | Estimate progress | Tantyahin ang progress |
| `predicted_progress` | Predicted Progress | Na-predict na Progress |
| `raw_prediction` | Raw prediction {raw:.2f}% capped to 0–100% for display. | Ang raw prediction na {raw:.2f}% ay nilimitahan sa 0–100% para sa display. |
| `outside_range` | This budget is outside the observed training range. | Labas ang budget na ito sa range ng training data. |
| `mse_note` | 20% holdout MSE: {mse:,.3f} squared percentage points · {count:,} training records after refit. Future forecasting accuracy is not established. | 20% holdout MSE: {mse:,.3f} squared percentage points · {count:,} training records pagkatapos ng refit. Hindi pa napatunayan ang accuracy sa pag-forecast ng hinaharap. |
| `footer` | TRACE · SDG 9 Infrastructure · SDG 16 Accountable Institutions · SDG 17 Partnerships | TRACE · SDG 9 Imprastraktura · SDG 16 Mga Institusyong May Pananagutan · SDG 17 Pagtutulungan |
| `column_contract_id` | Contract ID | Contract ID |
| `column_description` | Description | Description |
| `column_category` | Category | Kategorya |
| `column_contractor` | Contractor | Contractor |
| `column_province` | Province | Probinsya |
| `column_budget` | Budget | Budget |
| `column_progress` | Progress | Progress |
| `column_start` | Start Date | Petsa ng Pagsisimula |
| `column_completion` | Completion Date | Petsa ng Pagkakumpleto |
| `column_utilized` | Utilized Budget | Nagamit na Budget |
| `column_remaining` | Estimated Remaining Budget | Tantiyang Natitirang Budget |
| `column_projects` | Projects | Mga Project |
| `column_keyword` | Keyword | Keyword |
| `column_tfidf` | Mean TF-IDF | Average na TF-IDF |
| `column_measure` | Measure | Sukatan |
| `pie_hover` | %{label}<br>%{value:,} projects<br>%{percent}<extra></extra> | %{label}<br>%{value:,} project<br>%{percent}<extra></extra> |
| `choose_options` | Choose options | Pumili ng options |
| `chart_download` | Download plot as a PNG | I-download ang chart bilang PNG |
| `chart_zoom` | Zoom | Zoom |
| `chart_pan` | Pan | Igalaw ang chart |
| `chart_zoom_in` | Zoom in | Palakihin |
| `chart_zoom_out` | Zoom out | Paliitin |
| `chart_autoscale` | Autoscale | Awtomatikong ayusin ang scale |
| `chart_reset` | Reset axes | I-reset ang axes |
| `chart_spikes` | Toggle spike lines | I-on o i-off ang spike lines |
| `chart_closest` | Show closest data on hover | Ipakita ang pinakamalapit na data sa hover |
| `chart_compare` | Compare data on hover | Ihambing ang data sa hover |
| `chart_box` | Box Select | Pumili gamit ang kahon |
| `chart_lasso` | Lasso Select | Pumili gamit ang lasso |
| `native_download` | Download as CSV | I-download bilang CSV |
| `native_search` | Search | Maghanap |
| `native_fullscreen` | Fullscreen | Buong screen |
| `native_close` | Close | Isara |
| `native_clear` | Clear | I-clear |
| `native_no_rows` | No rows | Walang rows |
