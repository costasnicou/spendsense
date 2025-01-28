'use strict';
const show_wallet_btn = document.querySelector('.show-wallet');
const walletModal = document.querySelector('.wallet-modal');
const transModal = document.querySelector('.trans-modal');
const transferModal = document.querySelector('.transfer-modal');
const overlay = document.querySelector('.overlay');
const popupBtns = document.querySelectorAll('.toTop');
const filterTransModal = document.querySelector('.filter-trans-modal');
const transaction_type = document.querySelectorAll('.transaction-type');

// ------------OPEN MODALS----------------------//
// open wallet modal
const openWalletModal = function () {
  
  walletModal.classList.remove('hidden');
  overlay.classList.remove('hidden');
};

// open transactional modal
const openTransModal = function () {
  transModal.classList.remove('hidden');
  overlay.classList.remove('hidden');
};


// Open edit transaction modal dynamically based on transaction ID
const openEditTransModal = function (transactionId) {
  const editTransModal = document.getElementById(`editTransactionModal${transactionId}`); // Find the correct modal by ID
  if (editTransModal) {
    editTransModal.classList.remove('hidden');
    overlay.classList.remove('hidden');
  }
};


// Open edit Wallet modal dynamically based on transaction ID
const openEditWalletModal = function (walletId) {
  const editWalletModal = document.getElementById(`editWalletModal${walletId}`); // Find the correct modal by ID
  if (editWalletModal) {
    editWalletModal.classList.remove('hidden');
    overlay.classList.remove('hidden');
  }
};

const openTransferModal = function(){
  transferModal.classList.remove('hidden');
  overlay.classList.remove('hidden');
}

const openfilterTransModal = function(){
  filterTransModal.classList.remove('hidden');
  overlay.classList.remove('hidden');
}





// ------------OPEN MODALS----------------------//


//-----------CLOSE MODALS---------------------///


const closeModal = function (){
  walletModal.classList.add('hidden');
  filterTransModal.classList.add('hidden');
  transferModal.classList.add('hidden');
  transModal.classList.add('hidden');
  overlay.classList.add('hidden');
}


// Close edit transaction modal dynamically based on transaction ID
const closeEditWalletModal = function (walletId) {
  const editWalletModal = document.getElementById(`editWalletModal${walletId}`); // Find the correct modal by ID
  if (editWalletModal) {
    
    editWalletModal.classList.add('hidden');
    overlay.classList.add('hidden');
    
  }

  
};

// Close edit transaction modal dynamically based on transaction ID
const closeEditTransModal = function (transactionId) {
  const editTransModal = document.getElementById(`editTransactionModal${transactionId}`); // Find the correct modal by ID
  if (editTransModal) {
    editTransModal.classList.add('hidden');
    overlay.classList.add('hidden');
   
  }
};


//-----------CLOSE MODALS---------------------///


// disable editing for transfer


// recover fat amount
document.addEventListener('DOMContentLoaded', function () {
  const useFatCheckbox = document.querySelector('.form-check-input');
  const fatWalletField = document.querySelector('.field-fat_wallet');
  const fatWalletLabel = document.querySelector('.form-check-label');
  const checkBoxFormGroup = document.querySelector('.form-check-group')

  if (useFatCheckbox) {
      useFatCheckbox.addEventListener('change', function () {
          if (useFatCheckbox.checked) {
              fatWalletField.classList.remove('d-none');
              fatWalletLabel.classList.remove('d-none');
              checkBoxFormGroup.classList.remove('d-none');
          } else {
              fatWalletField.classList.add('d-none');
              fatWalletLabel.classList.add('d-none')
              checkBoxFormGroup.classList.add('d-none');
          }
      });
  }
});


// tabbed wallets
document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".tab");
  const tabContents = document.querySelectorAll(".tab-content");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      // Remove active class from all tabs and contents
      tabs.forEach(t => t.classList.remove("active"));
      tabContents.forEach(content => content.classList.remove("active"));

      // Add active class to the clicked tab and corresponding content
      tab.classList.add("active");
      const tabContent = document.querySelector(`#${tab.dataset.tab}`);
      tabContent.classList.add("active");
    });
  });
});