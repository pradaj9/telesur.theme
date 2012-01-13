// funcion utilizada por la view subscriptionform para validar el formulario 
// de subscriopcion al newsletter de imoko.
function Validar(){
    validar=true;
    if(document.Principal.correo.value.length==0){
        alert("Debe colocar una dirección valida de correo");
        document.Principal.correo.focus();
        return false;
    }

    if(document.Principal.$primer_nombre.value.length==0){
        alert("Debe colocar su nombre");
        document.Principal.$primer_nombre.focus();
        return false;
    }

    if(document.Principal.$primer_apellido.value.length==0){
        alert("Debe colocar su apellido");
        document.Principal.$primer_apellido.focus();
        return false;
    }

    return validar;
}
