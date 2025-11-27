// Funcionalidades específicas para el admin
document.addEventListener('DOMContentLoaded', function() {
    // Confirmación para eliminar
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que quieres eliminar este elemento? Esta acción no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });

    // Filtros en tablas
    const filterInputs = document.querySelectorAll('.filter-input');
    filterInputs.forEach(input => {
        input.addEventListener('input', function() {
            const filterValue = this.value.toLowerCase();
            const table = this.closest('table');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filterValue) ? '' : 'none';
            });
        });
    });

    // Estadísticas en tiempo real
    function updateStats() {
        fetch('/admin/api/stats/')
            .then(response => response.json())
            .then(data => {
                // Actualizar estadísticas en el dashboard
                document.querySelectorAll('.stat-number').forEach(stat => {
                    const statType = stat.closest('.stat-card').querySelector('h3').textContent;
                    // Actualizar según el tipo de estadística
                });
            });
    }

    // Actualizar estadísticas cada 30 segundos
    setInterval(updateStats, 30000);
});