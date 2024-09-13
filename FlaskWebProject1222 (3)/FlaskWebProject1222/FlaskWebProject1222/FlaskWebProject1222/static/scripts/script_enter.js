const submitButton = document.querySelector('.submit-button');

submitButton.addEventListener('click', function() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  if (email === '' || password === '') {
    alert('Пожалуйста, заполните все поля!');
    return;
  }
});