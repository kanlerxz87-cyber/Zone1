document.querySelectorAll('input.filter').forEach(function(input){
  input.addEventListener('input', function(){
    var q = input.value.trim().toLowerCase();
    var table = document.getElementById(input.dataset.target);
    if(!table) return;
    table.querySelectorAll('tbody tr').forEach(function(tr){
      tr.style.display = tr.textContent.toLowerCase().indexOf(q) === -1 ? 'none' : '';
    });
  });
});
