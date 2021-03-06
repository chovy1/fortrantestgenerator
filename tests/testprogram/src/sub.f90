MODULE sub

USE types
USE globals, ONLY : set, get, comm_variable, bv

IMPLICIT NONE

PRIVATE

INTEGER :: self

PUBLIC :: init, wrapper

CONTAINS

SUBROUTINE init(start)
  INTEGER, INTENT(in) :: start
  self = start
END SUBROUTINE init

FUNCTION wrapper(ra, rlog, av1, oreal, oa)
  TYPE(testa), INTENT(inout) :: ra
  LOGICAL, INTENT(in) :: rlog(4)
  CLASS(abstr), INTENT(inout) :: av1
  REAL, INTENT(out), OPTIONAL :: oreal
  TYPE(testa), INTENT(inout), OPTIONAL :: oa
  REAL :: wrapper

  wrapper = testsub(ra, rlog, av1, oreal, oa)
END FUNCTION wrapper

FUNCTION testsub(ra, rlog, av1, oreal, oa)

  TYPE(testa), INTENT(inout) :: ra
  LOGICAL, INTENT(in) :: rlog(4)
  CLASS(abstr), INTENT(inout) :: av1
  REAL, INTENT(out), OPTIONAL :: oreal
  TYPE(testa), INTENT(inout), OPTIONAL :: oa
  TYPE(jmodel) :: jm
#ifdef _OPENACC
  LOGICAL :: openacc
#endif
  REAL, POINTER :: testsub

  IF (rlog(1)) THEN
    ra%c%r2(:,:) = ra%b(1)%i2(1:2, 1:2) * ra%b(1)%i0 + ra%c%r2(:,:) + self + av1%deff()
    IF (rlog(2)) THEN
      ra%c%r2(:,:) = ra%c%r2(:,:) + bv(1)%bb(1)%p%deff()
    END IF
  END IF

  IF (PRESENT(oa)) THEN
    oa%c%r2(:,:) = oa%b(1)%i2(1:2, 1:2) * oa%b(1)%i0 + oa%c%r2(:,:)
    oa%c%r2(1,:) = oa%c%r2(1,:) + comm_variable(1)%grid_comm_pattern%send(1)%index_no(:)
  END IF

  CALL set(ra%c%r2(1,1))
  ALLOCATE(testsub)
  testsub = get()
  IF (PRESENT(oreal)) THEN
    oreal = testsub
  END IF

  jm = get_jmodel(1)
  WRITE (*,*) jm%name, ' : ', jm%id

#ifdef _OPENACC
  WRITE (*,*) 'OPENACC enabled'
#endif
END FUNCTION testsub

END MODULE sub
