"""File I/O utilities for macrocycle_design.

This module provides functions for reading and writing various file formats
used in macrocycle design, including PDB, MOL2, and other common formats.
"""

import os
import gzip
import bz2
import logging
from pathlib import Path
from typing import Union, IO, Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# File extensions for different compression formats
COMPRESSION_EXTENSIONS = {
    '.gz': 'gzip',
    '.bz2': 'bz2',
    '.zip': 'zip',
}

def get_file_handle(filename: Union[str, Path], mode: str = 'r') -> IO[Any]:
    """Get a file handle for reading or writing, with support for compression.
    
    Args:
        filename: Path to the file
        mode: File open mode ('r', 'w', 'a', etc.)
        
    Returns:
        File handle
    """
    filename = str(filename)
    
    # Determine if the file is compressed and get the appropriate opener
    _, ext = os.path.splitext(filename)
    compression = COMPRESSION_EXTENSIONS.get(ext.lower())
    
    if 'b' not in mode:
        # Add binary mode for compressed files if not already specified
        if compression:
            mode += 'b'
    
    # Open the file with the appropriate handler
    if compression == 'gzip':
        return gzip.open(filename, mode)
    elif compression == 'bz2':
        return bz2.open(filename, mode)
    else:
        # Regular file
        return open(filename, mode)

def read_pdb(filename: Union[str, Path]) -> Dict[str, Any]:
    """Read a PDB file and return its contents as a structured dictionary.
    
    Args:
        filename: Path to the PDB file
        
    Returns:
        Dictionary containing the PDB data
    """
    atoms = []
    header = []
    title = []
    remarks = []
    
    with get_file_handle(filename, 'r') as f:
        for line in f:
            if isinstance(line, bytes):
                line = line.decode('utf-8')
                
            record_type = line[0:6].strip()
            
            if record_type == 'ATOM' or record_type == 'HETATM':
                # Parse atom record
                atom = {
                    'record': record_type,
                    'serial': int(line[6:11]),
                    'name': line[12:16].strip(),
                    'alt_loc': line[16],
                    'res_name': line[17:20].strip(),
                    'chain_id': line[21],
                    'res_seq': int(line[22:26]),
                    'i_code': line[26],
                    'x': float(line[30:38]),
                    'y': float(line[38:46]),
                    'z': float(line[46:54]),
                    'occupancy': float(line[54:60]) if line[54:60].strip() else 1.0,
                    'temp_factor': float(line[60:66]) if line[60:66].strip() else 0.0,
                    'element': line[76:78].strip(),
                    'charge': line[78:80].strip()
                }
                atoms.append(atom)
                
            elif record_type == 'HEADER':
                header.append(line[10:].strip())
                
            elif record_type == 'TITLE':
                title.append(line[10:].strip())
                
            elif record_type == 'REMARK':
                remarks.append(line[10:].strip())
    
    return {
        'header': ' '.join(header),
        'title': ' '.join(title),
        'remarks': remarks,
        'atoms': atoms
    }

def write_pdb(filename: Union[str, Path], pdb_data: Dict[str, Any]) -> None:
    """Write a PDB file from a structured dictionary.
    
    Args:
        filename: Output PDB filename
        pdb_data: Dictionary containing PDB data
    """
    with get_file_handle(filename, 'w') as f:
        # Write header
        if 'header' in pdb_data and pdb_data['header']:
            f.write(f"HEADER    {pdb_data['header'][:40]}\n")
            
        # Write title
        if 'title' in pdb_data and pdb_data['title']:
            # Split title into lines of max 70 characters
            title = pdb_data['title']
            for i in range(0, len(title), 70):
                f.write(f"TITLE     {title[i:i+70]}\n")
        
        # Write remarks
        if 'remarks' in pdb_data and pdb_data['remarks']:
            for i, remark in enumerate(pdb_data['remarks'], 1):
                f.write(f"REMARK {i:3d} {remark}\n")
        
        # Write atoms
        if 'atoms' in pdb_data and pdb_data['atoms']:
            for atom in pdb_data['atoms']:
                record = atom.get('record', 'ATOM').ljust(6)
                serial = atom.get('serial', 1) % 100000
                name = atom.get('name', '').ljust(4)[:4]
                alt_loc = atom.get('alt_loc', ' ')
                res_name = atom.get('res_name', '').ljust(3)[:3]
                chain_id = atom.get('chain_id', 'A')
                res_seq = atom.get('res_seq', 1) % 10000
                i_code = atom.get('i_code', ' ')
                x = atom.get('x', 0.0)
                y = atom.get('y', 0.0)
                z = atom.get('z', 0.0)
                occupancy = atom.get('occupancy', 1.0)
                temp_factor = atom.get('temp_factor', 0.0)
                element = atom.get('element', '').ljust(2)[:2]
                charge = atom.get('charge', '  ').ljust(2)[:2]
                
                atom_line = (f"{record}{serial:5d} {name:4}{alt_loc}{res_name:3} {chain_id}{res_seq:4d}{i_code}   "
                           f"{x:8.3f}{y:8.3f}{z:8.3f}{occupancy:6.2f}{temp_factor:6.2f}          "
                           f"{element:>2}{charge}\n")
                f.write(atom_line)
        
        # Write end of file
        f.write("END\n")

def read_sequence_file(filename: Union[str, Path]) -> str:
    """Read a sequence from a FASTA or plain text file.
    
    Args:
        filename: Path to the sequence file
        
    Returns:
        str: Protein sequence in one-letter code
    """
    with get_file_handle(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # If it's a FASTA file, skip the header line(s)
    if lines and lines[0].startswith('>'):
        lines = lines[1:]
    
    # Join all lines and remove any non-letter characters
    sequence = ''.join(''.join(c for c in line if c.isalpha()).upper() for line in lines)
    
    return sequence
