import streamlit as st
import pandas as pd
from random import randint

# -----------------------------
# Setup
# -----------------------------
st.set_page_config(
    page_title="Homepage",
    page_icon="🧬",
)
proteins = ["A", "T", "G", "C", "*"]

# Initialize session state for org_dna
if "org_dna" not in st.session_state:
    st.session_state.org_dna = ""

st.title("🧬 PCR Simulator: Detect, Cut & Clone DNA")
st.write("This PCR simulator can create, analyze, and clone DNA sequences.")

# Load CSV file with error handling
try:
    df = pd.read_csv("DATA2.csv")  # Fixed path (use forward slashes)
    organisms = df["organism"].tolist()
except FileNotFoundError:
    st.error("Error: DATA2.csv file not found. Please check the file path.")
    st.stop()
except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.stop()

# Select pathogen
path_choice = st.selectbox("Choose a virus/bacteria:", organisms)
try:
    path_dna = df.loc[df["organism"] == path_choice, "dna_sequence"].values[0]
except IndexError:
    st.error(f"Error: No DNA sequence found for {path_choice} in the dataset.")
    st.stop()

org_choice = "Human"

# Function to generate random DNA sequence
def dna_seq_creator(chain_length=10):
    dna_seq = [proteins[randint(0, len(proteins)-1)] for _ in range(chain_length)]
    return "".join(dna_seq)

def is_valid_sequence(seq):
    allowed = set("eatcg*#n ")
    return all(ch in allowed for ch in seq.lower()) and len(seq) > 0

# Input DNA sequence
dna_input = st.text_input("Input your DNA segment (use A, T, G, C, #, *, N):", "")
if st.button("Submit DNA"):
    if is_valid_sequence(dna_input):
        st.session_state.org_dna = dna_input
        st.success(f"Valid input: {dna_input}")
    else:
        st.error("Invalid input. Please use only the letters A, T, G, C, *.")

# Generate random DNA sequence
if st.button("Generate DNA"):
    st.session_state.org_dna = dna_seq_creator(chain_length=len(path_dna) + 1)

# Reset DNA sequence
if st.button("Reset DNA"):
    st.session_state.org_dna = ""

# Function to validate DNA sequence
def is_valid_sequence(seq):
    allowed = set("ATCG*")  # Allow uppercase
    return all(ch in allowed for ch in seq) and len(seq) > 0


# Display results
st.markdown("---")
st.write(f"**{org_choice}'s DNA:** {st.session_state.org_dna}")
st.write(f"**{path_choice} DNA:** {path_dna}")

# PCR functions
def perform_denat(dna_seq):
    """Denaturation step"""
    if not dna_seq:
        return None, "Denaturation failed ❌ (no DNA sequence provided)"
    defec = dna_seq.count("*")
    ndefec = len(dna_seq) - defec
    if ndefec == 0:
        return None, "Denaturation failed ❌ (too many defective bases)"
    return dna_seq, "Denaturation successful ✅"

def get_complement(dna_seq):
    """Generate complementary DNA sequence"""
    comp_dna_seq = []
    for protein in dna_seq:
        if protein == "A":
            comp_dna_seq.append("T")
        elif protein == "T":
            comp_dna_seq.append("A")
        elif protein == "G":
            comp_dna_seq.append("C")
        elif protein == "C":
            comp_dna_seq.append("G")
        else:
            comp_dna_seq.append("*")
    return "".join(comp_dna_seq)

def perform_anl(comp_dna_seq_str, primer):
    """Annealing step"""
    if primer in comp_dna_seq_str:
        clone_point = comp_dna_seq_str.find(primer)
        return clone_point, "Annealing successful ✅ (primer attached)"
    return None, "Annealing failed ❌ (primer not found)"

def perform_ext(comp_dna_seq_str, clone_point):
    """Extension step"""
    clone_dna = comp_dna_seq_str[clone_point:]
    if "*" in clone_dna:
        error_point = clone_dna.find("*")
        clone_dna_fin = clone_dna[:error_point]
        return clone_dna_fin, "Extension successful ✅ (errors removed)"
    return clone_dna, "Extension successful ✅"

# Run PCR check
cycles = st.slider("How many cycles?", 1, 10, 3)
if st.button("🔬 Run PCR Check"):
    if not st.session_state.org_dna:
        st.error("No DNA sequence provided. Please generate or input a DNA sequence.")
    else:
        # Step 1: Denaturation
        dna_seq, msg = perform_denat(st.session_state.org_dna)
        st.info("Step 1: Denaturation")
        st.write(msg)


        # Infection check
        if path_dna in st.session_state.org_dna:
            st.error(f"Infection detected! {path_choice} DNA found inside {org_choice}.")
            cured_dna = st.session_state.org_dna.replace(path_dna, "")
            st.success(f"Pathogen DNA removed. Cured DNA: {cured_dna}")


            # Step 2: Annealing
            if dna_seq:
                comp_dna_seq_str = get_complement(dna_seq)
                st.success(f"Complementary DNA: {comp_dna_seq_str}")
                clone_point, msg = perform_anl(comp_dna_seq_str, path_dna)
                st.info("Step 2: Annealing")
                st.write(msg)

            if clone_point is not None:
                
                # Step 3: Extension
                req_dna, msg = perform_ext(comp_dna_seq_str, clone_point)
                st.info("Step 3: Extension")
                st.write(msg)

                st.success(f"Generated {cycles} clones:")
                for i in range(cycles):
                    st.text(f"Clone {i+1}: {req_dna}")
        else:
            st.success("No infection detected 🎉")