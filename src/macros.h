#ifndef NBFC_MACROS_H_
#define NBFC_MACROS_H_

#include <stddef.h>
#include <stdlib.h>

#define my               (*self)
#define max(A, B)        ((A) > (B) ? (A) : (B))
#define min(A, B)        ((A) < (B) ? (A) : (B))

#define ARRAY_SIZE(A)    (sizeof(A) / sizeof(*A))
#define ARRAY_SSIZE(A)   ((ssize_t) ARRAY_SIZE(A))
#define array_of(T)      array_of_ ## T

#define range(TYPE, VAR, START, STOP) \
  TYPE VAR = START; VAR < STOP; ++VAR

#define for_enumerate_array(TYPE, VAR, ARRAY) \
  for (range(TYPE, VAR, 0, (ARRAY).size))

#define for_each_array(TYPE, VAR, ARRAY) \
  for (TYPE VAR = (ARRAY).data; VAR != (ARRAY).data + (ARRAY).size; ++VAR)

#define for_each_array_reverse(TYPE, VAR, ARRAY) \
  for (TYPE VAR = (ARRAY).data + (ARRAY).size; --VAR != (ARRAY).data;)

#define declare_array_of(T)                  \
  typedef struct array_of(T) array_of(T);    \
  struct array_of(T) {                       \
    T*  data;                                \
    size_t size;                             \
  }

declare_array_of(float);

#ifndef NDEBUG
#define debug(...) fprintf(stderr, __VA_ARGS__)
#else
#define debug(...) (void)0
#endif

#endif
