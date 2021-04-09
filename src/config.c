#include "config.h"
#include "memory.h"
#include "stringbuf.h"
#include "nxjson_utils.h"

#include <limits.h>
#include <math.h>

#define str_Unset   NULL
#define int_Unset   INT_MIN
#define short_Unset SHRT_MIN
#define float_Unset NAN

static inline Error* bool_FromJson(bool* out, const nx_json* node) {
  if (node->type == NX_JSON_BOOL) {
    *out = node->val.u;
    return err_success();
  }
  return err_string(0, "Not a bool");
}

static inline Error* int_FromJson(int* out, const nx_json* node) {
  if (node->type == NX_JSON_INTEGER) {
    *out = node->val.i;
    return err_success();
  }
  return err_string(0, "Not a int");
}

static inline Error* short_FromJson(short* out, const nx_json* node) {
  int val = 0;
  Error* e = int_FromJson(&val, node);
  e_check();
  if (val < SHRT_MIN || val > SHRT_MAX)
    return err_string(0, "Value not in range for short type");
  *out = val;
  return err_success();
}

static inline Error* double_FromJson(double* out, const nx_json* node) {
  if (node->type == NX_JSON_INTEGER) {
    *out = node->val.i;
    return err_success();
  }
  if (node->type == NX_JSON_DOUBLE) {
    *out = node->val.dbl;
    return err_success();
  }
  return err_string(0, "Not a double");
}

static inline Error* float_FromJson(float* v, const nx_json* json) {
  double d = 0;
  Error* e = double_FromJson(&d, json);
  e_check();
  *v = d;
  return err_success();
}

static inline Error* Boolean_FromJson(Boolean* v, const nx_json* json) {
  return bool_FromJson((bool*) v, json);
}

static inline Error* str_FromJson(const char** v, const nx_json* json) {
  Error* e = nx_json_get_str(v, json);
  e_check();
  *v = Mem_Strdup(*v);
  return err_success();
}

static Error* RegisterWriteMode_FromJson(RegisterWriteMode* v, const nx_json* json) {
  const char* s = NULL;
  Error* e = nx_json_get_str(&s, json);
  if (e) return e;
  else if (!strcmp(s, "Set")) *v = RegisterWriteMode_Set;
  else if (!strcmp(s, "And")) *v = RegisterWriteMode_And;
  else if (!strcmp(s, "Or"))  *v = RegisterWriteMode_Or;
  else return err_string(0, "Invalid value for RegisterWriteMode");
  return e;
}

static Error* RegisterWriteOccasion_FromJson(RegisterWriteOccasion* v, const nx_json* json) {
  const char* s = NULL;
  Error* e = nx_json_get_str(&s, json);
  if (e) return e;
  else if (!strcmp(s, "OnWriteFanSpeed"))  *v = RegisterWriteOccasion_OnWriteFanSpeed;
  else if (!strcmp(s, "OnInitialization")) *v = RegisterWriteOccasion_OnInitialization;
  else return err_string(0, "Invalid value for RegisterWriteOccasion");
  return e;
}

static Error* OverrideTargetOperation_FromJson(OverrideTargetOperation* v, const nx_json* json) {
  const char* s = NULL;
  Error* e = nx_json_get_str(&s, json);
  if (e) return e;
  else if (!strcmp(s, "Read"))       *v = OverrideTargetOperation_Read;
  else if (!strcmp(s, "Write"))      *v = OverrideTargetOperation_Write;
  else if (!strcmp(s, "ReadWrite"))  *v = OverrideTargetOperation_ReadWrite;
  else return err_string(0, "Invalid value for OverrideTargetOperation");
  return e;
}

typedef Error* (FromJson_Callback)(void*, const nx_json*);

static Error* array_of_FromJson(FromJson_Callback callback, void** v_data, size_t* v_size, size_t size, const nx_json* json) {
  Error* e = nx_json_get_array(json);
  e_check();

  *v_size = 0;
  *v_data = Mem_Malloc(json->val.children.length, size);
  nx_json_for_each(child, json) {
    e = callback(((char*) *v_data) + size * *v_size, child);
    e_check();
    //(*v_size)++;
    *v_size = *v_size + 1;
  }
  return err_success();
}

#define define_array_of_T_FromJson(T) \
static inline Error* array_of_##T##_FromJson(array_of(T)* v, const nx_json *json) { \
  return array_of_FromJson((FromJson_Callback*) T ## _FromJson, (void**) &v->data, &v->size, sizeof(T), json); \
}

define_array_of_T_FromJson(float)
define_array_of_T_FromJson(TemperatureThreshold)
define_array_of_T_FromJson(FanConfiguration)
define_array_of_T_FromJson(FanSpeedPercentageOverride)
define_array_of_T_FromJson(RegisterWriteConfiguration)

static TemperatureThreshold Config_DefaultTemperatureThresholds_[] = {
  { 0,  0,   0},
  {60, 48,  10},
  {63, 55,  20},
  {66, 59,  50},
  {68, 63,  70},
  {71, 67, 100},
};

static array_of(TemperatureThreshold) Config_DefaultTemperatureThresholds = {
  Config_DefaultTemperatureThresholds_,
  ARRAY_SIZE(Config_DefaultTemperatureThresholds_)
};

#include "generated/config.generated.c"

// ============================================================================
// Validation code
// ============================================================================
//
// Calls *_ValidateFields on each structure and does some validations
// that cannot be auto-generated.

Error* Config_Validate(Config* c) {
  Error* e = NULL;
  char buf[128];
  StringBuf s = { buf, 0, sizeof(buf) - 1 };
  RegisterWriteConfiguration* r = NULL;
  FanConfiguration*           f = NULL;
  FanSpeedPercentageOverride* o = NULL;
  TemperatureThreshold*       t = NULL;

  e = Config_ValidateFields(c);
  e_goto(err);

  for_each_array(, r, c->RegisterWriteConfigurations) {
    e = RegisterWriteConfiguration_ValidateFields(r);
    e_goto(err);
  }
  r = NULL;

  for_each_array(, f, c->FanConfigurations) {
    e = FanConfiguration_ValidateFields(f);
    e_goto(err);

    for_each_array(, o, f->FanSpeedPercentageOverrides) {
      e = FanSpeedPercentageOverride_ValidateFields(o);
      e_goto(err);
    }
    o = NULL;

    bool has_0_FanSpeed   = false;
    bool has_100_FanSpeed = false;
    for_each_array(, t, f->TemperatureThresholds) {
      e = TemperatureThreshold_ValidateFields(t);
      e_goto(err);

      has_0_FanSpeed   |= (t->FanSpeed == 0);
      has_100_FanSpeed |= (t->FanSpeed == 100);

      if (t->UpThreshold < t->DownThreshold) {
        e = err_string(0, "UpThreshold must be greater than DownThreshold");
        goto err;
      }

      if (t->UpThreshold >= c->CriticalTemperature) {
        e = err_string(0, "UpThreshold must be lower than critical temperature");
        goto err;
      }

      for_each_array(TemperatureThreshold*, t1, f->TemperatureThresholds) {
        if (t != t1 && t->UpThreshold == t1->UpThreshold) {
          e = err_string(0, "Duplicate UpThreshold");
          goto err;
        }
      }
    }
    t = NULL;

    if (! has_0_FanSpeed) {
      e = err_string(0, "No threshold with FanSpeed == 0 found");
      goto err;
    }

    if (! has_100_FanSpeed) {
      e = err_string(0, "No threshold with FanSpeed == 100 found");
      goto err;
    }
  }

err:
  if (! e)
    return e;

  if (r) {
    StringBuf_Printf(&s, "RegisterWriteConfigurations[%td]",
        r - c->RegisterWriteConfigurations.data);
  }
  else if (f) {
    StringBuf_Printf(&s, "FanConfigurations[%td]: ",
        f - c->FanConfigurations.data);

    if (o)
      StringBuf_Printf(&s, "FanSpeedPercentageOverrides[%td]",
        o - f->FanSpeedPercentageOverrides.data);
    else if (t)
      StringBuf_Printf(&s, "TemperatureThresholds[%td]",
        t - f->TemperatureThresholds.data);
  }

  return err_string(e, Temp_Strdup(s.s));
}

Error* Config_FromFile(Config* config, const char* file) {
  const nx_json* js = NULL;
  Error* e = nx_json_parse_file(&js, file);
  e_check();
  return Config_FromJson(config, js);
}

