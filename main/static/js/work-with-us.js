document.addEventListener('DOMContentLoaded', function () {
    const emailBtn = document.getElementById('emailCopyBtn');
    
    if (emailBtn) {
        emailBtn.addEventListener('click', function () {
            const emailText = document.getElementById('targetEmail').innerText;
            
            navigator.clipboard.writeText(emailText).then(() => {
                const tooltip = document.getElementById('copyTooltip');
                tooltip.classList.add('show');
                
                setTimeout(() => {
                    tooltip.classList.remove('show');
                }, 2000);
            }).catch(err => {
                console.error('Kopyalama başarısız oldu: ', err);
            });
        });
    }
});