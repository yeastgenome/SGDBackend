function showAndClearField(frm){
  if (frm.firstName.value == "")
      alert("Hey! You didn't enter anything!")
  else
      alert("The field contains the text: " + frm.firstName.value)
  frm.firstName.value = ""
}