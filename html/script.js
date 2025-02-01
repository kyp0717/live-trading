function toggleModal(modalId) {
    const modal = document.getElementById(`modal-${modalId}`);
    const button = document.querySelector(`.card-container 
                                           .card:nth-child(${modalId}) 
                                           .card-button`);

    if (modal.style.display === "block") {
        modal.style.display = "none";
        button.textContent = "Read More...";
    } else {
        modal.style.display = "block";
        button.textContent = "Show Less...";
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(`modal-${modalId}`);
    modal.style.display = "none";
    const button = document.querySelector(`.card-container 
                .card:nth-child(${modalId}) .card-button`);
    button.textContent = "Read More...";
}