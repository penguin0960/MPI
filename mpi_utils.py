from mpi4py import MPI


def MPI_Send(comm: MPI.Intracomm, **kwargs):
    return comm.send(**kwargs)


def MPI_Ssend(comm: MPI.Intracomm, **kwargs):
    return comm.ssend(**kwargs)


def MPI_Bsend(comm: MPI.Intracomm, **kwargs):
    return comm.send(**kwargs)


def MPI_Rsend(comm: MPI.Intracomm, **kwargs):
    return comm.send(**kwargs)


def MPI_Isend(comm: MPI.Intracomm, **kwargs):
    return comm.isend(**kwargs)


def MPI_Issend(comm: MPI.Intracomm, **kwargs):
    return comm.issend(**kwargs)


def MPI_Ibsend(comm: MPI.Intracomm, **kwargs):
    return comm.isend(**kwargs)


def MPI_Irsend(comm: MPI.Intracomm, **kwargs):
    return comm.isend(**kwargs)
