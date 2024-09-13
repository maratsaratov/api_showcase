const submitButton = document.querySelector('.submit-button');

submitButton.addEventListener('click', function() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm-password').value;

  if (email === '' || password === '' || confirmPassword === '') {
    alert('Пожалуйста, заполните все поля!');
    return;
  }

  if (password !== confirmPassword) {
    alert('Пароли не совпадают!');
    return;
  }
});