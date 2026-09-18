import AnimalManager from "../../components/AnimalManager";

// Instituição (perfil "voluntario" no backend) pode cadastrar e editar
// animais, mas não excluir — regra de negócio do backend.
export default function OngAnimals() {
  return <AnimalManager podeExcluir={false} corTema="ong" />;
}
