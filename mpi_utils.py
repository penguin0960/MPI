from mpi4py import MPI


def send(comm: MPI.Intracomm, **kwargs):
    return comm.send(**kwargs)


def ssend(comm: MPI.Intracomm, **kwargs):
    return comm.ssend(**kwargs)


def bsend(comm: MPI.Intracomm, **kwargs):
    return comm.send(**kwargs)


def rsend(comm: MPI.Intracomm, **kwargs):
    return comm.send(**kwargs)


def isend(comm: MPI.Intracomm, **kwargs):
    return comm.isend(**kwargs)


def issend(comm: MPI.Intracomm, **kwargs):
    return comm.issend(**kwargs)


def ibsend(comm: MPI.Intracomm, **kwargs):
    return comm.isend(**kwargs)


def irsend(comm: MPI.Intracomm, **kwargs):
    return comm.isend(**kwargs)
