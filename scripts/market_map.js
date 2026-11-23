(() => {
  const sourceUrl = './data/analyst_assessments.json?v=' + Date.now();
  const escapeHtml = value => String(value || '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const displayDate = value => value ? new Intl.DateTimeFormat(undefined,{year:'numeric',month:'short',day:'numeric'}).format(new Date(value)) : 'not checked yet';
  const gartner2026 = ['Avature','Cornerstone','Darwinbox','Eightfold AI','Fountain','Greenhouse','iCIMS','Oracle','Phenom','SAP SuccessFactors','Workable','Workday'];
  fetch(sourceUrl, {cache:'no-store'}).then(response => {
    if (!response.ok) throw new Error('Analyst snapshot unavailable');
    return response.json();
  }).then(data => {
    const vendors = new Map();
    (data.vendors || []).forEach(vendor => {
      const previous = vendors.get(vendor.name) || {};
      vendors.set(vendor.name, {...previous, ...vendor});
    });
    gartner2026.forEach(name => {
      const vendor = vendors.get(name) || {name, segment:'Talent acquisition'};
      vendor.gartner2026 = vendor.gartner2026 || 'Included; placement not publicly stated';
      vendor.gartnerUrl = vendor.gartnerUrl || 'https://www.gartner.com/en/documents/7831517';
      vendors.set(name, vendor);
    });
    const allVendors = [...vendors.values()].sort((a,b) => a.name.localeCompare(b.name));
    document.getElementById('metric-vendors').textContent = allVendors.length;
    const profileCount = allVendors.filter(vendor => vendor.publicProfileSummary).length;
    const profileCheckedAt = data.profileCheckedAt || data.lastCheckedAt;
    document.getElementById('assessment-status').textContent = allVendors.length + ' providers · ' + profileCount + ' public profiles';
    document.getElementById('assessment-reports').innerHTML = (data.reports || []).map(report =>
      '<div class="assessment-report"><b>'+escapeHtml(report.analyst)+' · '+escapeHtml(report.year)+'</b><span>'+escapeHtml(report.title)+'</span><span>'+escapeHtml(report.publicNote)+'</span><span>Source link '+(report.sourceReachable ? 'checked' : 'check pending')+' · '+displayDate(report.lastCheckedAt || data.lastCheckedAt)+'</span><a href="'+escapeHtml(report.url)+'" target="_blank" rel="noopener">Open source ↗</a></div>'
    ).join('');
    const search = document.getElementById('vendor-search');
    const body = document.getElementById('assessment-rows');
    const render = () => {
      const query = search.value.trim().toLowerCase();
      const rows = allVendors.filter(vendor => (vendor.name+' '+vendor.segment+' '+(vendor.publicProfileSummary || '')).toLowerCase().includes(query));
      document.getElementById('vendor-count').textContent = 'Showing '+rows.length+' of '+allVendors.length+' providers';
      body.innerHTML = rows.map(vendor => {
        const evidence = [];
        if (vendor.gartner2026) evidence.push({label:'Gartner 2026: '+vendor.gartner2026, url:vendor.gartnerUrl});
        if (vendor.fosway2026) evidence.push({label:'Fosway 2026: '+vendor.fosway2026, url:vendor.foswayUrl});
        if (vendor.fosway2025) evidence.push({label:'Fosway 2025: '+vendor.fosway2025, url:vendor.foswayUrl});
        if (!evidence.length) evidence.push({label:'No public position located in the current source set'});
        const sourceLinks = evidence.filter(item => item.url).map(item => '<a href="'+escapeHtml(item.url)+'" target="_blank" rel="noopener">'+escapeHtml(item.label)+' ↗</a>').join('<br>');
        const profile = vendor.publicProfileSummary
          ? '<span>'+escapeHtml(vendor.publicProfileSummary)+'</span><small class="profile-meta">Official product page · checked '+escapeHtml(displayDate(vendor.profileCheckedAt || profileCheckedAt))+'</small>'
          : '<span class="assessment-empty">No readable public product summary found in the current source set</span>';
        const profileSource = vendor.profileUrl ? '<a href="'+escapeHtml(vendor.profileUrl)+'" target="_blank" rel="noopener">Official product page ↗</a>' : '<span class="assessment-empty">No official profile link located</span>';
        return '<tr><td><span class="vendor">'+escapeHtml(vendor.name)+'</span></td><td>'+escapeHtml(vendor.segment)+'</td><td class="profile-cell">'+profile+'</td><td>'+evidence.map(item => '<span class="assessment-badge">'+escapeHtml(item.label)+'</span>').join('')+'</td><td>'+profileSource+(sourceLinks ? '<br>'+sourceLinks : '')+'</td></tr>';
      }).join('') || '<tr><td colspan="5">No providers match this search.</td></tr>';
    };
    search.addEventListener('input', render);
    render();
  }).catch(() => {
    document.getElementById('assessment-status').textContent = 'Assessment snapshot unavailable';
    document.getElementById('assessment-rows').innerHTML = '<tr><td colspan="4">The analyst assessment and market-map snapshot could not be loaded.</td></tr>';
  });
})();
